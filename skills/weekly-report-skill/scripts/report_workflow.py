#!/usr/bin/env python3
"""Local, dependency-free goal tracking and human confirmation for periodic reports."""
import argparse
import calendar
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, timezone

VERSION = 1
BASE_FIELDS = ("title", "department", "owner", "criteria", "deadline", "start_date", "parent_id", "metric")
STATES = ("not_started", "in_progress", "completed", "paused", "cancelled")
LABELS = {
    "title": "目标名称", "department": "责任部门", "owner": "负责人", "criteria": "验收标准",
    "deadline": "截止日期", "start_date": "开始日期", "parent_id": "上级目标 ID", "metric": "指标口径",
    "status": "完成状态", "progress": "实际进展与交付结果", "actual": "实际数值",
    "actual_date": "实际完成日期", "forecast_date": "预计完成日期", "reason": "偏差原因",
    "action": "纠偏动作", "action_owner": "纠偏负责人", "action_deadline": "纠偏截止日期",
    "next_plan": "下期计划", "change_reason": "变更原因", "confirmation": "目标与节点确认",
}
STATE_LABELS = dict(zip(STATES, ("未启动", "进行中", "已完成", "暂停", "取消")))


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def present(value):
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def load(path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else copy.deepcopy(default)


def atomic_text(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".writing-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            out.write(text)
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def save(path, value):
    atomic_text(path, json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n")


def number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("必须是有限数值")
    return value


def day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("日期须为 YYYY-MM-DD")
    return date.fromisoformat(value)


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
        raise ValueError("ID 须由字母、数字、短横线或下划线组成，最长 80 字符")
    return value


def validate_metric(metric):
    if metric is None:
        return
    if not isinstance(metric, dict):
        raise ValueError("metric 须为对象或 null")
    number(metric["target"])
    for key in ("unit", "definition", "period_start", "period_end"):
        if not present(metric.get(key)):
            raise ValueError(f"指标缺少 {key}")
    if day(metric["period_start"]) > day(metric["period_end"]):
        raise ValueError("指标统计周期倒置")
    if metric.get("direction") not in ("at_least", "at_most"):
        raise ValueError("指标 direction 须为 at_least 或 at_most")
    if metric.get("aggregation") not in ("incremental", "cumulative", "snapshot"):
        raise ValueError("指标 aggregation 须为 incremental、cumulative 或 snapshot")


def validate_goal(goal):
    identifier(goal["id"])
    if not isinstance(goal.get("title"), str) or not present(goal["title"]):
        raise ValueError("目标必须有名称")
    for key in ("department", "owner", "criteria", "parent_id"):
        if goal.get(key) is not None and not isinstance(goal[key], str):
            raise ValueError(f"{key} 须为文字或 null")
    for key in ("deadline", "start_date"):
        if present(goal.get(key)):
            day(goal[key])
    if goal.get("deadline") and goal.get("start_date") and day(goal["start_date"]) > day(goal["deadline"]):
        raise ValueError("目标开始日期晚于截止日期")
    validate_metric(goal.get("metric"))


def validate_period(period):
    identifier(period["id"])
    if period.get("type") not in ("weekly", "monthly"):
        raise ValueError("报告类型须为 weekly 或 monthly")
    if not day(period["start"]) <= day(period["as_of"]) <= day(period["end"]):
        raise ValueError("统计截止日须在报告起止日期之间")


def state_dir(workdir):
    return Path(workdir).resolve() / ".weekly-report"


def session_path(workdir, period):
    return state_dir(workdir) / "periods" / identifier(period) / "session.json"


@contextmanager
def locked(workdir):
    # OS lock releases on crash, unlike a sentinel lock file. Windows uses msvcrt.
    root = state_dir(workdir)
    root.mkdir(parents=True, exist_ok=True)
    with (root / ".lock").open("a+b") as handle:
        if os.name == "nt":
            import msvcrt
            handle.write(b"0")
            handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(handle, fcntl.LOCK_EX)
        try:
            yield
        finally:
            if os.name == "nt":
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def ledger_for(workdir):
    return load(state_dir(workdir) / "ledger.json", {"schema_version": VERSION, "revision": 0, "goals": []})


def field(name, scope="observation", kind="text", value=None, **extra):
    return {"key": name, "label": LABELS.get(name, name), "scope": scope, "kind": kind,
            "value": value, **extra}


def task(tid, title, group, fields, goal=None, context=None, priority="高"):
    return {"id": tid, "title": title, "group": group, "goal_id": goal.get("id") if goal else None,
            "department": (goal or {}).get("department") or "待确认", "priority": priority,
            "context": context or {}, "fields": fields}


def comparison_scope(metric, obs):
    keys = ("unit", "definition", "aggregation", "period_start", "period_end")
    return all(present(obs.get(key)) and obs[key] == metric[key] for key in keys)


def make_tasks(session, old_goals):
    tasks = []
    if not session["goals"]:
        tasks.append(task("setup", "建立本期目标和时间节点", "目标基线确认", [
            field("setup", "extra", label="请添加目标；确实没有目标时选择暂无法提供并说明原因")]))
    for goal in session["goals"]:
        gid = goal["id"]
        old = old_goals.get(gid)
        changed = old is None or any(goal.get(k) != old.get(k) for k in BASE_FIELDS)
        baseline = []
        for key in ("department", "owner", "criteria", "deadline"):
            if not present(goal.get(key)):
                baseline.append(field(key, "goal", "date" if key == "deadline" else "text"))
        if changed:
            baseline.insert(0, field("confirmation", "control", "confirm"))
            if old:
                baseline.append(field("change_reason", "control"))
        if baseline:
            tasks.append(task(f"baseline-{gid}", goal["title"], "目标基线确认", baseline, goal,
                              {"原目标": old, "本次目标": goal}))
        obs = session["observations"].get(gid, {})
        missing = []
        for key in ("status", "progress"):
            if not present(obs.get(key)):
                missing.append(field(key, kind="status" if key == "status" else "text"))
        if not obs.get("actual_date"):
            missing.append(field("actual_date", kind="date", when="completed"))
        for key in ("reason", "action", "action_owner", "action_deadline", "forecast_date"):
            if not present(obs.get(key)):
                missing.append(field(key, kind="date" if key.endswith("date") or key.endswith("deadline") else "text", when="deviation"))
        if missing:
            tasks.append(task(f"progress-{gid}", goal["title"], "里程碑与部门计划", missing, goal,
                              {"目标": goal, "已有进展": obs}))
        metric = goal.get("metric")
        if metric:
            metric_fields = []
            if not present(obs.get("actual")):
                metric_fields.append(field("actual", kind="number"))
            for key, label in (("unit", "单位"), ("definition", "统计口径"), ("aggregation", "数值类型"),
                               ("period_start", "统计起始日"), ("period_end", "统计截止日")):
                if not present(obs.get(key)) or obs[key] != metric[key]:
                    kind = "date" if key.startswith("period_") else "aggregation" if key == "aggregation" else "text"
                    metric_fields.append(field(key, kind=kind, value=obs.get(key), label=label))
            if metric_fields:
                tasks.append(task(f"metric-{gid}", goal["title"], "指标数据", metric_fields, goal,
                                  {"目标口径": metric, "已有数据": obs}))
    for item in session.get("questions", []):
        identifier(item["id"])
        tasks.append(task(item["id"], item["title"], item.get("group", "风险与资料异常"),
                          [field("answer", "extra", label=item["question"])],
                          context={"说明": item.get("context", "")}, priority=item.get("priority", "中")))
    ids = [t["id"] for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("补充问题 ID 重复")
    # Retain conditional questions: editing a proposed deadline/status can activate them.
    return tasks


def field_active(session, t, f):
    if f.get("key") == "setup" and session.get("new_goals"):
        return False
    if not f.get("when"):
        return True
    obs = session["observations"].get(t["goal_id"], {}).copy()
    for candidate in session.get("tasks", [t]):
        if candidate.get("goal_id") != t["goal_id"]:
            continue
        for key, a in session.get("answers", {}).get(candidate["id"], {}).items():
            if a.get("mode") == "value":
                obs[key] = a.get("value")
            elif a.get("mode") == "unknown":
                obs.pop(key, None)
    if f["when"] == "completed":
        return obs.get("status") == "completed"
    goal = next(g for g in session["goals"] if g["id"] == t["goal_id"])
    deadline = goal.get("deadline")
    for candidate in session.get("tasks", []):
        if candidate.get("goal_id") == t["goal_id"]:
            a = session.get("answers", {}).get(candidate["id"], {}).get("deadline", {})
            if a.get("mode") == "value":
                deadline = a.get("value")
    metric = goal.get("metric")
    metric_missed = False
    if metric and comparison_scope(metric, obs) and isinstance(obs.get("actual"), (int, float)):
        metric_missed = obs["actual"] < metric["target"] if metric["direction"] == "at_least" else obs["actual"] > metric["target"]
    # String order is safe for already validated ISO dates, including partial drafts.
    return metric_missed or obs.get("status") in ("paused", "cancelled") or bool(deadline and (
        (obs.get("status") != "completed" and deadline < session["period"]["as_of"])
        or (obs.get("status") == "completed" and obs.get("actual_date") and obs["actual_date"] > deadline)
        or (obs.get("forecast_date") and obs["forecast_date"] > deadline)))


def validate_observation(obs, period):
    if obs.get("status") is not None and obs["status"] not in STATES:
        raise ValueError("无效完成状态")
    for key in ("actual_date", "forecast_date", "action_deadline", "period_start", "period_end"):
        if present(obs.get(key)):
            day(obs[key])
    if obs.get("actual_date") and day(obs["actual_date"]) > day(period["as_of"]):
        raise ValueError("实际完成日期不能晚于统计截止日")
    if present(obs.get("actual")):
        number(obs["actual"])
    if obs.get("period_start") and obs.get("period_end"):
        if day(obs["period_start"]) > day(obs["period_end"]):
            raise ValueError("实际统计周期倒置")
        if day(obs["period_end"]) > day(period["as_of"]):
            raise ValueError("实际数据截止日不能晚于报告统计截止日")


def prepare(workdir, data):
    validate_period(data["period"])
    path = session_path(workdir, data["period"]["id"])
    with locked(workdir):
        if path.exists():
            raise ValueError("本期会话已存在；使用 status/serve 恢复。新增材料请使用新的修订周期 ID。")
        ledger = ledger_for(workdir)
        old = {g["id"]: g for g in ledger["goals"]}
        goals = {k: copy.deepcopy(v) for k, v in old.items() if v.get("lifecycle", "active") == "active"}
        goals.update(copy.deepcopy(ledger.get("pending_goals", {})))
        supplied = set()
        for raw in data.get("goals", []):
            validate_goal(raw)
            if raw["id"] in supplied:
                raise ValueError("目标 ID 重复")
            supplied.add(raw["id"])
            goals[raw["id"]] = {**copy.deepcopy(old.get(raw["id"], {})),
                                **{k: v for k, v in raw.items() if k in BASE_FIELDS or k == "id"}}
        observations = copy.deepcopy(data.get("observations", {}))
        for gid, obs in observations.items():
            if gid not in goals:
                if gid in old:
                    goals[gid] = copy.deepcopy(old[gid])
                else:
                    raise ValueError(f"进展关联到不存在的目标：{gid}")
            validate_observation(obs, data["period"])
        session = {"schema_version": VERSION, "period": data["period"], "base_revision": ledger["revision"],
                   "goals": list(goals.values()), "observations": observations,
                   "questions": data.get("questions", []), "sources": data.get("sources", []),
                   "notes": data.get("notes", {}), "answers": {}, "new_goals": [], "revision": 0,
                   "created_at": now(), "status": "draft"}
        session["tasks"] = make_tasks(session, old)
        if not any(field_active(session, t, f) for t in session["tasks"] for f in t["fields"]):
            session["status"] = "ready"
        save(path, session)
        return session


def check_answer(f, answer):
    if not isinstance(answer, dict):
        return "请填写答案或明确选择暂无法提供"
    if answer.get("mode") == "unknown":
        return None if isinstance(answer.get("reason"), str) and answer["reason"].strip() else "暂无法提供时须说明原因"
    if answer.get("mode") != "value" or not present(answer.get("value")):
        return "请填写答案或明确选择暂无法提供"
    value = answer["value"]
    try:
        if f["kind"] == "number":
            number(value)
        elif f["kind"] == "date":
            day(value)
        elif f["kind"] == "status" and value not in STATES:
            raise ValueError("请选择有效状态")
        elif f["kind"] == "aggregation" and value not in ("incremental", "cumulative", "snapshot"):
            raise ValueError("请选择有效数值类型")
        elif f["kind"] == "confirm" and value is not True:
            raise ValueError("请逐项确认目标，或选择暂无法确认并说明原因")
        elif f["kind"] == "text" and not isinstance(value, str):
            raise ValueError("请输入文字")
    except (ValueError, TypeError) as exc:
        return str(exc)
    return None


def resolve(session):
    resolved = copy.deepcopy(session)
    goals = {g["id"]: g for g in resolved["goals"]}
    resolved["unresolved"] = []
    resolved["extra_answers"] = []
    for t in session["tasks"]:
        for f in t["fields"]:
            if not field_active(session, t, f):
                continue
            answer = session["answers"].get(t["id"], {}).get(f["key"], {})
            if answer.get("mode") == "unknown":
                resolved["unresolved"].append({"task_id": t["id"], "goal_id": t["goal_id"],
                    "title": t["title"], "field": f["key"], "label": f["label"], "scope": f["scope"],
                    "reason": answer.get("reason"), "group": t["group"]})
                if f["scope"] == "observation":
                    resolved["observations"].setdefault(t["goal_id"], {}).pop(f["key"], None)
                continue
            if answer.get("mode") != "value":
                continue
            value = answer["value"]
            if f["scope"] == "goal":
                goals[t["goal_id"]][f["key"]] = value
            elif f["scope"] == "observation":
                resolved["observations"].setdefault(t["goal_id"], {})[f["key"]] = value
            elif f["scope"] == "extra":
                resolved["extra_answers"].append({"title": t["title"], "answer": value, "group": t["group"]})
    for raw in session.get("new_goals", []):
        goal = {k: copy.deepcopy(v) for k, v in raw.items() if k not in ("observation", "confirmed")}
        goals[goal["id"]] = goal
        resolved["observations"][goal["id"]] = raw.get("observation", {})
    resolved["goals"] = list(goals.values())
    return resolved


def submission_errors(session):
    errors = []
    for t in session["tasks"]:
        for f in t["fields"]:
            if not field_active(session, t, f):
                continue
            error = check_answer(f, session["answers"].get(t["id"], {}).get(f["key"]))
            if error:
                errors.append({"task_id": t["id"], "field": f["key"], "message": error})
    existing = {g["id"] for g in session["goals"]}
    new_ids = set()
    for g in session.get("new_goals", []):
        try:
            validate_goal(g)
            if g["id"] in existing | new_ids:
                raise ValueError("新增目标 ID 重复")
            new_ids.add(g["id"])
            if g.get("confirmed") is not True:
                raise ValueError("请确认新增目标")
            for key in ("department", "owner", "criteria", "deadline"):
                if not present(g.get(key)):
                    raise ValueError(f"新增目标缺少 {LABELS[key]}")
            validate_observation(g.get("observation", {}), session["period"])
            if not all(present(g.get("observation", {}).get(k)) for k in ("status", "progress")):
                raise ValueError("新增目标须填写本期状态与进展")
            if g["observation"]["status"] == "completed" and not g["observation"].get("actual_date"):
                raise ValueError("新增已完成目标须填写实际完成日期")
            if g.get("metric") and not (present(g["observation"].get("actual")) and comparison_scope(g["metric"], g["observation"])):
                raise ValueError("新增指标目标须填写数值和匹配的统计口径；复杂指标请保存草稿后由 agent 建立修订会话")
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"task_id": "new-goals", "field": g.get("id", ""), "message": str(exc)})
    resolved = resolve(session)
    for goal in resolved["goals"]:
        try:
            validate_goal(goal)
            validate_observation(resolved["observations"].get(goal["id"], {}), session["period"])
        except (ValueError, KeyError, TypeError) as exc:
            errors.append({"task_id": f"progress-{goal['id']}", "field": "", "message": str(exc)})
    return errors


def update_session(workdir, period, payload, submit=False):
    path = session_path(workdir, period)
    with locked(workdir):
        session = load(path)
        if session is None:
            raise ValueError("本期会话不存在")
        if session["status"] not in ("draft", "ready"):
            raise ValueError("本期已提交，请勿重复修改")
        if payload.get("revision") != session["revision"]:
            raise ValueError("草稿已被另一页面更新，请刷新后重试")
        if not isinstance(payload.get("answers"), dict) or not isinstance(payload.get("new_goals", []), list):
            raise ValueError("answers 须为对象，new_goals 须为数组")
        candidate = copy.deepcopy(session)
        candidate["answers"] = payload["answers"]
        candidate["new_goals"] = payload.get("new_goals", [])
        # Reject malformed nested answers even for a partial draft.
        valid_fields = {t["id"]: {f["key"] for f in t["fields"]} for t in session["tasks"]}
        for tid, answers in candidate["answers"].items():
            if tid not in valid_fields or not isinstance(answers, dict) or set(answers) - valid_fields[tid]:
                raise ValueError("包含不存在的补充问题")
            if any(not isinstance(a, dict) for a in answers.values()):
                raise ValueError("补充答案格式错误")
        if any(not isinstance(g, dict) for g in candidate["new_goals"]):
            raise ValueError("新增目标格式错误")
        errors = submission_errors(candidate) if submit else []
        if errors:
            return {"ok": False, "errors": errors}
        candidate["revision"] += 1
        candidate["updated_at"] = now()
        if submit:
            candidate["status"] = "submitted"
            candidate["submitted_at"] = now()
        save(path, candidate)
        return {"ok": True, "revision": candidate["revision"], "status": candidate["status"]}


def analyze(session):
    rows = []
    as_of = day(session["period"]["as_of"])
    for goal in session["goals"]:
        gid = goal["id"]
        obs = session["observations"].get(gid, {})
        unknowns = [u for u in session.get("unresolved", []) if u["goal_id"] == gid]
        baseline_unknown = any(u["scope"] in ("goal", "control") for u in unknowns)
        unknown_fields = {u["field"] for u in unknowns}
        confirmed = not baseline_unknown
        state = obs.get("status")
        deadline = goal.get("deadline")
        actual_date = obs.get("actual_date")
        forecast = obs.get("forecast_date")
        schedule = "unknown"
        delay = None
        if confirmed and deadline:
            due = day(deadline)
            if state == "completed" and actual_date:
                delay = (day(actual_date) - due).days
                schedule = "early" if delay < 0 else "on_time" if delay == 0 else "late"
            elif state in ("not_started", "in_progress", "paused"):
                if as_of > due:
                    schedule, delay = "overdue", (as_of - due).days
                elif forecast and day(forecast) > due:
                    schedule, delay = "at_risk", (day(forecast) - due).days
                else:
                    schedule = "not_due"
        metric_result = None
        metric = goal.get("metric")
        if metric and confirmed and present(obs.get("actual")) and comparison_scope(metric, obs):
            target, actual = metric["target"], obs["actual"]
            metric_result = {"target": target, "actual": actual, "difference": actual - target,
                             "met": actual >= target if metric["direction"] == "at_least" else actual <= target,
                             "completion_rate": (actual / target * 100) if metric["direction"] == "at_least" and target > 0 else None}
        fact_complete = confirmed and state is not None and present(obs.get("progress")) and not unknown_fields.intersection({"status", "progress"})
        result = "unknown"
        if fact_complete:
            if state == "cancelled":
                result = "cancelled"
            elif metric and metric_result is None:
                result = "unknown"
            elif schedule in ("overdue", "late", "at_risk") or state == "paused" or (metric_result and not metric_result["met"]):
                result = "deviation"
            elif state == "completed" or (metric_result and metric_result["met"]):
                result = "achieved"
            else:
                result = "in_progress"
        rows.append({"goal": goal, "observation": obs, "baseline_confirmed": confirmed,
                     "result": result, "schedule": schedule, "delay_days": delay,
                     "original_delay_days": (day(actual_date or forecast) - day(goal["original_deadline"])).days
                     if goal.get("original_deadline") and (actual_date or forecast) and confirmed else None,
                     "metric_comparison": metric_result, "unresolved": unknowns})
    counts = {k: sum(row["result"] == k for row in rows)
              for k in ("achieved", "deviation", "in_progress", "cancelled", "unknown")}
    return {"period": session["period"], "counts": counts, "tracked": len(rows), "items": rows,
            "unresolved": session.get("unresolved", []), "notes": session.get("notes", {}),
            "extra_answers": session.get("extra_answers", [])}


def confirmation_markdown(session):
    lines = [f"# 人工补充与确认记录 — {session['period']['id']}", "", f"提交状态：{session['status']}", ""]
    for t in session["tasks"]:
        lines.extend([f"## {t['title']}（{t['group']}）", "", f"责任部门：{t['department']}", ""])
        for f in t["fields"]:
            if not field_active(session, t, f):
                continue
            answer = session["answers"].get(t["id"], {}).get(f["key"], {})
            value = ("暂无法提供：" + answer.get("reason", "")) if answer.get("mode") == "unknown" else answer.get("value", "尚未回答")
            if value is True:
                value = "已确认"
            lines.extend([f"- {f['label']}：{value}", ""])
    if not session["tasks"]:
        lines.append("材料完整，本期无补充问题。")
    for g in session.get("new_goals", []):
        lines.extend([f"## 新增目标：{g['title']}", "", f"负责人：{g['owner']}；截止日期：{g['deadline']}", ""])
    return "\n".join(lines) + "\n"


def merge(workdir, period):
    path = session_path(workdir, period)
    with locked(workdir):
        session = load(path)
        if session is None:
            raise ValueError("本期会话不存在")
        if session["status"] in ("merged", "generated"):
            return load(path.parent / "analysis.json")
        if session["status"] not in ("ready", "submitted"):
            raise ValueError("等待浏览器逐项确认并提交，不得生成最终报告")
        errors = submission_errors(session)
        if errors:
            raise ValueError(json.dumps(errors, ensure_ascii=False))
        resolved = resolve(session)
        ledger = ledger_for(workdir)
        commit_id = session["created_at"] + ":" + period
        if ledger.get("last_commit") != commit_id:
            if ledger["revision"] != session["base_revision"]:
                raise ValueError("目标台账已更新，请基于最新台账建立修订周期并重新确认")
            old = {g["id"]: g for g in ledger["goals"]}
            blocked = {u["goal_id"] for u in resolved["unresolved"] if u["scope"] in ("goal", "control")}
            pending = copy.deepcopy(ledger.get("pending_goals", {}))
            for g in resolved["goals"]:
                gid = g["id"]
                if gid in blocked:
                    pending[gid] = copy.deepcopy(g)
                    continue
                pending.pop(gid, None)
                previous = old.get(gid)
                history = copy.deepcopy((previous or {}).get("history", []))
                before = {k: (previous or {}).get(k) for k in BASE_FIELDS}
                after = {k: g.get(k) for k in BASE_FIELDS}
                if previous is None or before != after:
                    answer = session["answers"].get(f"baseline-{gid}", {}).get("change_reason", {})
                    history.append({"at": now(), "period": period, "before": before if previous else None,
                                    "after": after, "reason": answer.get("value", "首次确认")})
                g["history"] = history
                g["original_deadline"] = (previous or {}).get("original_deadline", g.get("deadline"))
                observation = resolved["observations"].get(gid, {})
                complete_facts = not any(u["goal_id"] == gid for u in resolved["unresolved"])
                g["lifecycle"] = "closed" if complete_facts and observation.get("status") in ("completed", "cancelled") and present(observation.get("progress")) else "active"
                old[gid] = copy.deepcopy(g)
            ledger.update(goals=list(old.values()), pending_goals=pending, revision=ledger["revision"] + 1, last_commit=commit_id)
            # Persist the resulting ledger with the immutable period inputs before committing.
            save(path.parent / "snapshot.json", {"session": resolved, "ledger_after": ledger})
            save(state_dir(workdir) / "ledger.json", ledger)
        else:
            # Recover a crash after ledger commit but before session/analysis writes.
            snapshot = load(path.parent / "snapshot.json")
            resolved = snapshot["session"]
        analysis = analyze(resolved)
        analysis["analyzed_at"] = now()
        analysis["ledger_revision"] = ledger["revision"]
        analysis["history_comparisons"] = historical_comparisons(workdir, analysis)
        save(path.parent / "analysis.json", analysis)
        atomic_text(path.parent / "confirmation.md", confirmation_markdown(session))
        session.update(status="merged", merged_at=now())
        save(path, session)
        return analysis


def historical_comparisons(workdir, analysis):
    """Only compare disjoint, complete periods of the same reporting type and metric scope."""
    current = analysis["period"]
    if current["as_of"] != current["end"]:
        return []
    candidates = []
    for path in (state_dir(workdir) / "periods").glob("*/analysis.json"):
        past = load(path)
        p = past["period"]
        if p["type"] == current["type"] and p["end"] < current["start"] and p["as_of"] == p["end"]:
            candidates.append(past)
    if not candidates:
        return []
    past = max(candidates, key=lambda x: (x["period"]["end"], x.get("ledger_revision", 0)))
    old_rows = {r["goal"]["id"]: r for r in past["items"]}
    results = []
    for row in analysis["items"]:
        old = old_rows.get(row["goal"]["id"])
        if not old or not old["metric_comparison"] or not row["metric_comparison"]:
            continue
        m1, m0 = row["goal"]["metric"], old["goal"]["metric"]
        # Cumulative values across different windows have no default period-over-period meaning.
        if m1["aggregation"] == "cumulative" or any(m1[k] != m0[k] for k in ("unit", "definition", "aggregation", "direction")):
            continue
        a1, a0 = row["observation"], old["observation"]
        if m1["aggregation"] == "incremental":
            def whole_month(obs):
                start, end = day(obs["period_start"]), day(obs["period_end"])
                return start.day == 1 and start.year == end.year and start.month == end.month and end.day == calendar.monthrange(end.year, end.month)[1]
            calendar_months = current["type"] == "monthly" and whole_month(a1) and whole_month(a0)
            if not calendar_months and (day(a1["period_end"]) - day(a1["period_start"])).days != (day(a0["period_end"]) - day(a0["period_start"])).days:
                continue
        delta = a1["actual"] - a0["actual"]
        results.append({"goal_id": row["goal"]["id"], "previous_period": past["period"]["id"],
                        "difference": delta, "change_rate": delta / abs(a0["actual"]) * 100 if a0["actual"] != 0 else None})
    return results


def finalize(workdir, period, report):
    path = session_path(workdir, period)
    with locked(workdir):
        session = load(path)
        if session is None or session["status"] not in ("merged", "generated"):
            raise ValueError("请先完成确认和 merge")
        content = Path(report).read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError("报告不能为空")
        if session["status"] == "generated":
            if (path.parent / "report.md").read_text(encoding="utf-8") != content:
                raise ValueError("本期报告已归档；修改请创建修订周期")
            return session
        atomic_text(path.parent / "report.md", content)
        session.update(status="generated", generated_at=now(), report_sha256=hashlib.sha256(content.encode()).hexdigest())
        save(path, session)
        return session


def status(workdir, period):
    path = session_path(workdir, period)
    session = load(path)
    if session is None:
        raise ValueError("本期会话不存在")
    return {"period": session["period"], "status": session["status"], "revision": session["revision"],
            "tasks": sum(any(field_active(session, t, f) for f in t["fields"]) for t in session["tasks"]),
            "errors": submission_errors(session) if session["status"] == "draft" else [],
            "directory": str(path.parent)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("prepare", "serve", "status", "validate", "merge", "finalize"):
        p = sub.add_parser(name)
        p.add_argument("--workdir", required=True)
        if name == "prepare":
            p.add_argument("--input", required=True)
        else:
            p.add_argument("--period", required=True)
        if name == "serve":
            p.add_argument("--port", type=int, default=0)
            p.add_argument("--no-browser", action="store_true")
        if name == "finalize":
            p.add_argument("--report", required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            result = prepare(args.workdir, load(Path(args.input)))
            result = {k: result[k] for k in ("status", "period", "tasks")}
        elif args.command == "serve":
            from supplement_server import serve
            serve(args.workdir, args.period, args.port, not args.no_browser)
            return
        elif args.command == "status":
            result = status(args.workdir, args.period)
        elif args.command == "validate":
            session = load(session_path(args.workdir, args.period))
            if session is None:
                raise ValueError("本期会话不存在")
            result = {"errors": submission_errors(session)}
        elif args.command == "merge":
            result = merge(args.workdir, args.period)
        else:
            result = finalize(args.workdir, args.period, args.report)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        if args.command == "validate" and result["errors"]:
            sys.exit(1)
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
