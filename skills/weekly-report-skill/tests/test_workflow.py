import json
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import report_workflow as w
from supplement_server import make_server


def goal(gid="G1", **overrides):
    return {"id": gid, "title": "客户验收", "department": "研发", "owner": "张工",
            "criteria": "客户签署验收单", "deadline": "2026-10-25", "metric": None, **overrides}


def period(pid="2026-W42", **overrides):
    return {"id": pid, "type": "weekly", "start": "2026-10-12", "end": "2026-10-18", "as_of": "2026-10-18", **overrides}


def observation(**overrides):
    return {"status": "in_progress", "progress": "联调完成，等待验收", **overrides}


def input_data(goals=None, observations=None, p=None):
    return {"period": p or period(), "goals": [goal()] if goals is None else goals,
            "observations": {"G1": observation()} if observations is None else observations}


def acknowledge(session, unknown=None):
    """Fixture answers: no real user data is auto-confirmed by production code."""
    values = {"confirmation": True, "change_reason": "客户要求调整", "status": "in_progress",
              "progress": "完成联调", "reason": "客户环境未开放", "action": "协调环境",
              "action_owner": "李经理", "action_deadline": "2026-10-19", "forecast_date": "2026-10-20",
              "actual_date": "2026-10-16", "actual": 0}
    answers = {}
    for t in session["tasks"]:
        answers[t["id"]] = {}
        for f in t["fields"]:
            key = f["key"]
            a = {"mode": "value", "value": values.get(key, "人工确认内容")}
            if unknown and (t["id"], key) in unknown:
                a = {"mode": "unknown", "reason": "等待客户回复"}
            answers[t["id"]][key] = a
    return {"revision": session["revision"], "answers": answers, "new_goals": []}


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="report-test-")
        self.work = self.temp.name

    def tearDown(self):
        self.temp.cleanup()

    def submit(self, session, payload=None):
        result = w.update_session(self.work, session["period"]["id"], payload or acknowledge(session), True)
        self.assertTrue(result["ok"], result)
        return w.merge(self.work, session["period"]["id"])

    def test_first_baseline_and_missing_goal_are_separate(self):
        s = w.prepare(self.work, input_data([goal(), goal("G2", title="展会材料")], {}))
        self.assertEqual(s["status"], "draft")
        ids = {t["id"] for t in s["tasks"]}
        self.assertTrue({"baseline-G1", "baseline-G2", "progress-G1", "progress-G2"} <= ids)
        with self.assertRaisesRegex(ValueError, "等待浏览器"):
            w.merge(self.work, s["period"]["id"])
        with self.assertRaisesRegex(ValueError, "已存在"):
            w.prepare(self.work, input_data())

    def test_unknown_is_not_failure_and_not_defaulted(self):
        s = w.prepare(self.work, input_data(observations={}))
        p = acknowledge(s, {("progress-G1", "status"), ("progress-G1", "progress")})
        result = self.submit(s, p)
        self.assertEqual(result["counts"]["unknown"], 1)
        self.assertEqual(result["counts"]["deviation"], 0)
        self.assertEqual(result["items"][0]["schedule"], "unknown")
        self.assertEqual(len(result["unresolved"]), 2)
        record = (w.session_path(self.work, s["period"]["id"]).parent / "confirmation.md").read_text()
        self.assertIn("等待客户回复", record)

    def test_unknown_requires_reason_and_blocks_submit(self):
        s = w.prepare(self.work, input_data())
        p = acknowledge(s)
        p["answers"]["baseline-G1"]["confirmation"] = {"mode": "unknown", "reason": " "}
        self.assertFalse(w.update_session(self.work, s["period"]["id"], p, True)["ok"])
        self.assertEqual(w.load(w.session_path(self.work, s["period"]["id"]))["status"], "draft")

    def test_save_revision_resume_and_post_submit_lock(self):
        s = w.prepare(self.work, input_data())
        p = {"revision": 0, "answers": {}, "new_goals": []}
        self.assertEqual(w.update_session(self.work, s["period"]["id"], p)["revision"], 1)
        with self.assertRaisesRegex(ValueError, "另一页面"):
            w.update_session(self.work, s["period"]["id"], p)
        restored = w.load(w.session_path(self.work, s["period"]["id"]))
        self.submit(restored)
        with self.assertRaisesRegex(ValueError, "已提交"):
            w.update_session(self.work, s["period"]["id"], acknowledge(restored))

    def test_complete_existing_material_skips_browser_and_carries_missing_goal(self):
        self.submit(w.prepare(self.work, input_data()))
        s = w.prepare(self.work, input_data(goals=[], p=period("next")))
        self.assertEqual(s["status"], "ready")
        w.merge(self.work, "next")
        s2 = w.prepare(self.work, input_data(goals=[], observations={}, p=period("third")))
        self.assertEqual(s2["status"], "draft")
        self.assertIn("progress-G1", {t["id"] for t in s2["tasks"]})

    def test_date_change_keeps_original_and_merge_is_idempotent(self):
        self.submit(w.prepare(self.work, input_data()))
        s = w.prepare(self.work, input_data([goal(deadline="2026-10-30")], p=period("r2")))
        self.submit(s)
        first = w.ledger_for(self.work)
        second_analysis = w.merge(self.work, "r2")
        self.assertEqual(first, w.ledger_for(self.work))
        g = first["goals"][0]
        self.assertEqual(g["original_deadline"], "2026-10-25")
        self.assertEqual(g["deadline"], "2026-10-30")
        self.assertEqual(g["history"][-1]["reason"], "客户要求调整")
        self.assertEqual(len(g["history"]), 2)
        self.assertEqual(second_analysis["tracked"], 1)

    def test_unconfirmed_baseline_persists_for_next_period(self):
        s = w.prepare(self.work, input_data())
        result = self.submit(s, acknowledge(s, {("baseline-G1", "confirmation")}))
        self.assertFalse(result["items"][0]["baseline_confirmed"])
        self.assertEqual(w.ledger_for(self.work)["goals"], [])
        s2 = w.prepare(self.work, input_data(goals=[], observations={}, p=period("next")))
        self.assertEqual(s2["goals"][0]["id"], "G1")
        self.assertIn("baseline-G1", {t["id"] for t in s2["tasks"]})

    def test_schedule_and_no_linear_assumption(self):
        r = w.analyze({**input_data([goal()], {"G1": observation()}), "unresolved": []})
        self.assertEqual(r["items"][0]["schedule"], "not_due")
        self.assertEqual(r["items"][0]["result"], "in_progress")
        for completed, expected in (("2026-10-15", "early"), ("2026-10-16", "on_time"), ("2026-10-17", "late")):
            r = w.analyze({**input_data([goal(deadline="2026-10-16")], {"G1": observation(status="completed", actual_date=completed)}), "unresolved": []})
            self.assertEqual(r["items"][0]["schedule"], expected)
        r = w.analyze({**input_data([goal(deadline="2026-10-16")], {"G1": observation()}), "unresolved": []})
        self.assertEqual(r["items"][0]["delay_days"], 2)
        self.assertEqual(r["items"][0]["result"], "deviation")

    def test_dynamic_completed_and_overdue_fields(self):
        s = w.prepare(self.work, input_data(observations={}))
        p = acknowledge(s)
        p["answers"]["progress-G1"]["status"] = {"mode": "value", "value": "completed"}
        p["answers"]["progress-G1"].pop("actual_date")
        result = w.update_session(self.work, s["period"]["id"], p, True)
        self.assertTrue(any(e["field"] == "actual_date" for e in result["errors"]))
        p["answers"]["progress-G1"]["actual_date"] = {"mode": "value", "value": "2026-10-19"}
        self.assertFalse(w.update_session(self.work, s["period"]["id"], p, True)["ok"])

    def test_zero_lower_is_better_and_scope_mismatch(self):
        metric = {"target": 0, "unit": "次", "definition": "事故次数", "direction": "at_most", "aggregation": "incremental", "period_start": "2026-10-12", "period_end": "2026-10-18"}
        obs = observation(actual=0, **{k:v for k,v in metric.items() if k not in ("target", "direction")})
        data = {**input_data([goal(metric=metric)], {"G1": obs}), "unresolved": []}
        r = w.analyze(data)["items"][0]["metric_comparison"]
        self.assertTrue(r["met"])
        self.assertIsNone(r["completion_rate"])
        data["observations"]["G1"]["unit"] = "万元"
        self.assertIsNone(w.analyze(data)["items"][0]["metric_comparison"])

    def test_concurrent_periods_do_not_overwrite_ledger(self):
        s1 = w.prepare(self.work, input_data())
        s2 = w.prepare(self.work, input_data(p=period("second")))
        self.submit(s1)
        w.update_session(self.work, "second", acknowledge(s2), True)
        with self.assertRaisesRegex(ValueError, "台账已更新"):
            w.merge(self.work, "second")

    def test_commit_recovery_and_report_archive(self):
        s = w.prepare(self.work, input_data())
        self.submit(s)
        path = w.session_path(self.work, s["period"]["id"])
        stored = w.load(path)
        stored["status"] = "submitted"
        w.save(path, stored)
        ledger = w.ledger_for(self.work)
        w.merge(self.work, s["period"]["id"])
        self.assertEqual(w.ledger_for(self.work), ledger)
        report = Path(self.work) / "report.md"
        report.write_text("# 周报\n\n客户验收进行中。", encoding="utf-8")
        w.finalize(self.work, s["period"]["id"], report)
        self.assertEqual(w.status(self.work, s["period"]["id"])["status"], "generated")
        report.write_text("不同内容", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "已归档"):
            w.finalize(self.work, s["period"]["id"], report)

    def test_setup_add_goal(self):
        s = w.prepare(self.work, input_data(goals=[], observations={}))
        g = goal()
        g.update(confirmed=True, observation=observation())
        self.submit(s, {"revision": 0, "answers": {}, "new_goals": [g]})
        self.assertEqual(w.ledger_for(self.work)["goals"][0]["id"], "G1")

    def test_cumulative_history_and_overlapping_periods_not_added(self):
        metric = {"target":100,"unit":"万元","definition":"验收金额","direction":"at_least","aggregation":"cumulative","period_start":"2026-10-01","period_end":"2026-10-11"}
        obs = observation(actual=20, **{k:v for k,v in metric.items() if k not in ("target","direction")})
        s = w.prepare(self.work, input_data([goal(metric=metric)], {"G1":obs}, period("previous",start="2026-10-05",end="2026-10-11",as_of="2026-10-11")))
        self.submit(s)
        metric2 = {**metric,"period_end":"2026-10-18"}
        obs2 = {**obs,"actual":40,"period_end":"2026-10-18"}
        r = self.submit(w.prepare(self.work, input_data([goal(metric=metric2)], {"G1":obs2})))
        self.assertEqual(r["items"][0]["metric_comparison"]["actual"], 40)
        self.assertEqual(r["history_comparisons"], [])

    def test_invalid_input_does_not_create_session(self):
        for data in (input_data(p=period("../escape")), input_data(p=period(as_of="2026-11-01")), input_data(observations={"missing":observation()}), input_data(observations={"G1":observation(actual=float("nan"))})):
            with self.assertRaises((ValueError, KeyError)):
                w.prepare(self.work, data)
        self.assertFalse(w.session_path(self.work, "2026-W42").exists())

    def test_incomplete_completion_remains_active_for_followup(self):
        s = w.prepare(self.work, input_data(observations={"G1":observation(status="completed")}))
        self.submit(s, acknowledge(s, {("progress-G1","actual_date")}))
        self.assertEqual(w.ledger_for(self.work)["goals"][0]["lifecycle"], "active")

    def test_goal_input_cannot_reset_original_deadline(self):
        self.submit(w.prepare(self.work, input_data()))
        raw = goal(deadline="2026-10-30",original_deadline="2026-10-30",history=[])
        s = w.prepare(self.work, input_data([raw], p=period("r2")))
        self.submit(s)
        self.assertEqual(w.ledger_for(self.work)["goals"][0]["original_deadline"], "2026-10-25")

    def test_metric_shortfall_activates_correction_questions(self):
        metric={"target":100,"unit":"万元","definition":"验收金额","direction":"at_least","aggregation":"incremental","period_start":"2026-10-12","period_end":"2026-10-18"}
        obs=observation(actual=90, **{k:v for k,v in metric.items() if k not in ("target","direction")})
        s=w.prepare(self.work,input_data([goal(metric=metric)],{"G1":obs}))
        task=next(t for t in s["tasks"] if t["id"]=="progress-G1")
        self.assertTrue(w.field_active(s,task,next(f for f in task["fields"] if f["key"]=="reason")))

    def test_comparable_history_uses_latest_revision_and_zero_base(self):
        metric={"target":100,"unit":"万元","definition":"验收金额","direction":"at_least","aggregation":"incremental","period_start":"2026-10-05","period_end":"2026-10-11"}
        obs=observation(actual=0, **{k:v for k,v in metric.items() if k not in ("target","direction")})
        for pid,actual in (("previous",20),("previous-r2",0)):
            old_period=period(pid,start="2026-10-05",end="2026-10-11",as_of="2026-10-11")
            self.submit(w.prepare(self.work,input_data([goal(metric=metric)],{"G1":{**obs,"actual":actual}},old_period)))
        metric2={**metric,"period_start":"2026-10-12","period_end":"2026-10-18"}
        obs2={**obs,"actual":40,"period_start":"2026-10-12","period_end":"2026-10-18"}
        result=self.submit(w.prepare(self.work,input_data([goal(metric=metric2)],{"G1":obs2})))
        trend=result["history_comparisons"][0]
        self.assertEqual(trend["previous_period"],"previous-r2")
        self.assertEqual(trend["difference"],40)
        self.assertIsNone(trend["change_rate"])

    def test_monthly_comparison_supports_different_calendar_month_lengths(self):
        for pid,start,end,actual in (("202608","2026-08-01","2026-08-31",100),("202609","2026-09-01","2026-09-30",120)):
            p=period(pid,type="monthly",start=start,end=end,as_of=end)
            metric={"target":100,"unit":"万元","definition":"验收金额","direction":"at_least","aggregation":"incremental","period_start":start,"period_end":end}
            obs=observation(actual=actual,**{k:v for k,v in metric.items() if k not in ("target","direction")})
            result=self.submit(w.prepare(self.work,input_data([goal(metric=metric,deadline="2026-10-25")],{"G1":obs},p)))
        self.assertEqual(result["history_comparisons"][0]["difference"],20)
        self.assertEqual(result["history_comparisons"][0]["change_rate"],20)


class HTTPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="report-http-")
        self.s = w.prepare(self.temp.name, input_data())
        self.server, self.url = make_server(self.temp.name, self.s["period"]["id"])
        self.token = self.url.split("token=",1)[1]
        self.base = self.url.split("/#",1)[0]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def request(self, route, payload=None, token=True, **headers):
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Content-Type":"application/json", **headers}
        if token:
            headers["X-Session-Token"] = self.token
        try:
            with urlopen(Request(self.base + route, data=body, headers=headers), timeout=5) as response:
                return response.status, response.read(), response.headers
        except HTTPError as exc:
            return exc.code, exc.read(), exc.headers

    def test_assets_auth_and_cross_origin(self):
        code, body, headers = self.request("/")
        self.assertEqual(code, 200)
        self.assertIn("汇报工作台", body.decode())
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(self.request("/api/session", token=False)[0], 403)
        self.assertEqual(self.request("/api/session")[0], 200)
        self.assertEqual(self.request("/api/draft", acknowledge(self.s), Origin="https://example.com")[0], 403)
        self.assertEqual(self.request("/../../ledger.json")[0], 404)

    def test_http_invalid_draft_resume_and_submit(self):
        pid = self.s["period"]["id"]
        code, _, _ = self.request("/api/submit", {"revision":0,"answers":{},"new_goals":[]})
        self.assertEqual(code, 422)
        self.assertEqual(self.request("/api/draft", {"revision":0,"answers":{},"new_goals":[]})[0], 200)
        s = json.loads(self.request("/api/session")[1])
        self.assertEqual(s["revision"], 1)
        self.assertEqual(self.request("/api/submit", acknowledge(s))[0], 200)
        self.assertEqual(w.status(self.temp.name, pid)["status"], "submitted")
        self.assertEqual(w.merge(self.temp.name, pid)["tracked"], 1)


if __name__ == "__main__":
    unittest.main()
