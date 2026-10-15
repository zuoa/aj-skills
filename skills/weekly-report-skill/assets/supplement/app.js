"use strict";
const token = new URLSearchParams(location.hash.slice(1)).get("token") || "";
const $ = id => document.getElementById(id);
let session, selectedGroup = "", dirty = false, busy = false, savedLabel = "尚未修改";
const states = {not_started:"未启动",in_progress:"进行中",completed:"已完成",paused:"暂停",cancelled:"取消"};
const aggregations = {incremental:"本期新增",cumulative:"截至本期累计",snapshot:"截止日快照"};
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function markDirty() { dirty = true; savedLabel = "有修改尚未保存"; $("save-state").textContent = savedLabel; updateCoverage(); }
async function request(route, body) {
  const response = await fetch(route, {method:body ? "POST":"GET", headers:{"X-Session-Token":token,"Content-Type":"application/json"}, body:body ? JSON.stringify(body):undefined});
  const data = await response.json();
  if (!response.ok && !data.errors) throw new Error(data.error || "连接失败，请重试");
  return data;
}
function currentObs(task) {
  const obs = {...(session.observations[task.goal_id] || {})};
  for (const t of session.tasks.filter(t => t.goal_id === task.goal_id)) {
    for (const [key, a] of Object.entries(session.answers[t.id] || {})) {
      if (a.mode === "value") obs[key] = a.value;
      else if (a.mode === "unknown") delete obs[key];
    }
  }
  return obs;
}
function active(t, f) {
  if (f.key === "setup" && session.new_goals.length) return false;
  if (!f.when) return true;
  const obs = currentObs(t);
  if (f.when === "completed") return obs.status === "completed";
  let due = session.goals.find(g => g.id === t.goal_id)?.deadline;
  for (const bt of session.tasks.filter(bt => bt.goal_id === t.goal_id)) {
    const a = session.answers[bt.id]?.deadline;
    if (a?.mode === "value") due = a.value;
  }
  const metric=session.goals.find(g => g.id === t.goal_id)?.metric;
  const comparable=metric && ['unit','definition','aggregation','period_start','period_end'].every(k=>obs[k]===metric[k]);
  const missed=comparable && typeof obs.actual==='number' && (metric.direction==='at_least'?obs.actual<metric.target:obs.actual>metric.target);
  return missed || ["paused","cancelled"].includes(obs.status) || Boolean(due && ((obs.status !== "completed" && due < session.period.as_of) || (obs.status === "completed" && obs.actual_date > due) || obs.forecast_date > due));
}
function answered(t, f) {
  if (!active(t, f)) return true;
  const a = session.answers[t.id]?.[f.key];
  if (a?.mode === "unknown") return Boolean(a.reason?.trim());
  if (a?.mode !== "value") return false;
  if (f.kind === "confirm") return a.value === true;
  return a.value !== null && a.value !== undefined && String(a.value).trim() !== "";
}
function taskDone(t) { return t.fields.every(f => answered(t,f)); }
function visibleTasks() { return session.tasks.filter(t => t.fields.some(f => active(t,f))); }
function updateCoverage() {
  const tasks = visibleTasks(), done = tasks.filter(taskDone).length;
  $("coverage").textContent = `${done} / ${tasks.length}`;
  $("progress").max = Math.max(tasks.length, 1); $("progress").value = done;
  document.querySelectorAll("[data-task]").forEach(el => {
    const t = tasks.find(t => t.id === el.dataset.task);
    if (!t) return;
    el.classList.toggle("done", taskDone(t));
    const badge = el.querySelector(".badge");
    badge.textContent = taskDone(t) ? "已回应" : `${t.priority}优先级`; badge.classList.toggle("done", taskDone(t));
  });
}
function inspect(value) {
  if (value == null) return "未提供";
  if (typeof value !== "object") return states[value] || aggregations[value] || String(value);
  const names = {title:"目标",department:"部门",owner:"负责人",criteria:"验收标准",deadline:"截止日期",original_deadline:"原始截止日期",metric:"指标",status:"状态",progress:"进展",actual:"实际值",target:"目标值",unit:"单位",definition:"口径",aggregation:"数值类型",period_start:"统计起始",period_end:"统计截止",forecast_date:"预计完成",actual_date:"实际完成",reason:"原因",direction:"达标方向"};
  return Object.entries(value).filter(([k]) => !["history","sources","lifecycle","id","parent_id"].includes(k)).map(([k,v]) => `${names[k] || k}：${inspect(v)}`).join("\n");
}
function question(t,f) {
  const wrap = node("div",undefined,"question"); wrap.id = `q-${t.id}-${f.key}`; wrap.hidden = !active(t,f);
  const id = `input-${t.id}-${f.key}`, a = session.answers[t.id]?.[f.key] || {};
  const label = node("label",f.label); label.htmlFor = id; wrap.append(label);
  let input;
  if (f.kind === "status" || f.kind === "aggregation") {
    input = node("select"); input.append(new Option("请选择", ""));
    for (const [v,l] of Object.entries(f.kind === "status" ? states : aggregations)) input.append(new Option(l,v));
  } else if (["number","date","confirm"].includes(f.kind)) {
    input = node("input"); input.type = f.kind === "confirm" ? "checkbox" : f.kind;
    if (f.kind === "number") input.step = "any";
  } else input = node("textarea");
  input.id = id;
  const value = a.mode === "value" ? a.value : f.value;
  if (f.kind === "confirm") input.checked = value === true;
  else input.value = value ?? "";
  const control = f.kind === "confirm" ? node("div",undefined,"confirm") : node("div");
  control.append(input);
  if (f.kind === "confirm") { const l = node("label","已核对该目标、验收标准和时间节点"); l.htmlFor = id; control.append(l); }
  wrap.append(control);
  if (f.when) wrap.append(node("p",f.when === "completed" ? "选择已完成后，需要确认实际完成日期。" : "延期、暂停或取消事项，需要确认原因与后续安排。","hint"));
  const unknownRow = node("div",undefined,"unknown"), unknown = node("input");
  unknown.type = "checkbox"; unknown.id = `unknown-${t.id}-${f.key}`; unknown.checked = a.mode === "unknown";
  const unknownLabel = node("label",f.kind === "confirm" ? "暂无法确认" : "暂无法提供"); unknownLabel.htmlFor = unknown.id;
  unknownRow.append(unknown, unknownLabel); wrap.append(unknownRow);
  const reason = node("textarea",undefined,"reason"); reason.placeholder = "说明原因，例如：尚未收到验收反馈，预计周五补齐";
  reason.setAttribute("aria-label",`${t.title}：${f.label}暂无法提供的原因`); reason.value = a.reason || "";
  wrap.append(reason);
  function sync() { control.hidden = unknown.checked; reason.hidden = !unknown.checked; }
  sync();
  function store() {
    session.answers[t.id] ||= {};
    let v = f.kind === "confirm" ? input.checked : input.value;
    if (f.kind === "number") v = input.value === "" ? null : Number(input.value);
    session.answers[t.id][f.key] = unknown.checked ? {mode:"unknown",reason:reason.value} : {mode:"value",value:v};
    sync(); markDirty();
    // Update conditional fields without replacing the focused input.
    for (const task of session.tasks) for (const field of task.fields) {
      const el = $(`q-${task.id}-${field.key}`); if (el) el.hidden = !active(task,field);
    }
    document.querySelectorAll("[data-task]").forEach(el => {
      const task = session.tasks.find(task => task.id === el.dataset.task);
      el.hidden = !task.fields.some(field => active(task,field));
    });
  }
  input.addEventListener("input",store); reason.addEventListener("input",store); unknown.addEventListener("change",store);
  return wrap;
}
function card(t) {
  const el = node("section",undefined,"card"); el.dataset.task = t.id; el.id = `task-${t.id}`;
  const head = node("div",undefined,"card-head"), titles = node("div");
  titles.append(node("p",`${t.group} · ${t.department}`,"kicker"),node("h2",t.title)); head.append(titles,node("span",`${t.priority}优先级`,"badge")); el.append(head);
  const g = session.goals.find(g => g.id === t.goal_id);
  if (g) { const strip = node("div",undefined,"goal-strip"); strip.append(node("span",`负责人 ${g.owner || "待确认"}`),node("span",`截止 ${g.deadline || "待确认"}`)); if (g.original_deadline && g.original_deadline !== g.deadline) strip.append(node("span",`原始截止 ${g.original_deadline}`)); el.append(strip); }
  if (Object.keys(t.context).length) { const details = node("details",undefined,"context"); details.append(node("summary","查看已有材料和目标口径")); const dl = node("dl"); for (const [k,v] of Object.entries(t.context)) dl.append(node("dt",k),node("dd",inspect(v))); details.append(dl); el.append(details); }
  for (const f of t.fields) el.append(question(t,f));
  el.hidden = !t.fields.some(f => active(t,f));
  return el;
}
function renderCards() {
  const dept = $("department").value, priority = $("priority").value, completion = $("completion").value;
  const tasks = session.tasks.filter(t => (!selectedGroup || t.group === selectedGroup) && (!dept || t.department === dept) && (!priority || t.priority === priority) && (!completion || taskDone(t) === (completion === "done")));
  $("cards").replaceChildren(...tasks.map(card));
  if (!tasks.length) $("cards").append(node("p","当前筛选下没有待处理事项。可调整筛选，或补充新目标。","empty"));
  updateCoverage();
}
function renderGroups() {
  $("groups").replaceChildren();
  for (const name of ["",...new Set(session.tasks.map(t=>t.group))]) {
    const b = node("button",name || "全部补充事项"); b.type = "button"; b.classList.toggle("active",selectedGroup === name);
    b.addEventListener("click",()=>{selectedGroup=name;renderGroups();renderCards();}); $("groups").append(b);
  }
}
function renderNewGoals() {
  $("new-goals").replaceChildren();
  session.new_goals.forEach((g,index)=>{
    const el = node("section",undefined,"new-card"), remove = node("button","移除该目标","secondary"); remove.type = "button";
    remove.addEventListener("click",()=>{session.new_goals.splice(index,1);markDirty();renderNewGoals();renderCards();}); el.append(remove);
    const grid = node("div",undefined,"new-fields");
    const specs = [["title","目标名称","text"],["department","责任部门","text"],["owner","负责人","text"],["deadline","截止日期","date"],["criteria","验收标准 / 预期结果","textarea"],["status","本期状态","status"],["progress","本期进展（下期新计划请写明尚未启动）","textarea"],["actual_date","实际完成日期（已完成时填写）","date"]];
    for (const [key,name,kind] of specs) {
      const wrapper = node("div",undefined,kind === "textarea" ? "wide" : ""), label = node("label",name), inObs = ["status","progress","actual_date"].includes(key);
      let input = node(kind === "textarea" ? "textarea" : kind === "status" ? "select" : "input");
      input.id = `new-${g.id}-${key}`; label.htmlFor = input.id;
      if (kind === "status") { input.append(new Option("请选择","")); for (const [v,l] of Object.entries(states)) input.append(new Option(l,v)); }
      else if (kind !== "textarea") input.type = kind;
      input.value = (inObs ? g.observation?.[key] : g[key]) || "";
      input.addEventListener("input",()=>{if (inObs) {g.observation ||= {};g.observation[key]=input.value;} else g[key]=input.value;markDirty();}); wrapper.append(label,input); grid.append(wrapper);
    }
    el.append(grid);
    const confirm = node("label",undefined,"unknown"), cb=node("input");cb.type="checkbox";cb.checked=g.confirmed===true;
    cb.addEventListener("change",()=>{g.confirmed=cb.checked;markDirty();});confirm.append(cb,node("span","确认将该目标及时间节点纳入持续跟踪"));el.append(confirm);$("new-goals").append(el);
  });
}
function showErrors(errors) {
  const box=$("errors");box.hidden=false;box.replaceChildren(node("strong","还有事项需要确认，已保留本次填写："));
  const list=node("ul");
  errors.forEach(e=>{const li=node("li"),link=node("a",e.message); const target=$(`q-${e.task_id}-${e.field}`)||$(`task-${e.task_id}`)||$("new-goals");link.href=`#${target.id}`;target.classList.add("invalid");link.addEventListener("click",ev=>{ev.preventDefault();selectedGroup="";$("department").value="";$("priority").value="";$("completion").value="";renderGroups();renderCards();const fresh=$(`q-${e.task_id}-${e.field}`)||$(`task-${e.task_id}`)||$("new-goals");fresh.classList.add("invalid");fresh.scrollIntoView({block:"center"});fresh.querySelector("input,textarea,select")?.focus();});li.append(link);list.append(li);});box.append(list);box.scrollIntoView({block:"center"});
}
async function persist(submit) {
  if (busy) return; busy=true;$("save").disabled=true;$("submit").disabled=true;
  try {
    const result=await request(submit?"/api/submit":"/api/draft",{revision:session.revision,answers:session.answers,new_goals:session.new_goals});
    if (result.errors) { showErrors(result.errors);return; }
    session.revision=result.revision;session.status=result.status;dirty=false;$("errors").hidden=true;
    savedLabel=submit?"确认已提交":"草稿已保存";$("save-state").textContent=savedLabel;
    if(submit) { $("message").textContent="补充已提交，当前会话将继续分析并生成报告。若会话已中断，请再次调用该 skill，继续本期报告。";lockForm(); }
  } catch(error) {$("message").textContent=error.message;} finally {busy=false;if(["draft","ready"].includes(session.status)){$("save").disabled=false;$("submit").disabled=false;}}
}
function lockForm() {document.querySelectorAll("input,textarea,select,button").forEach(el=>el.disabled=true);}
async function init() {
  try {
    session=await request("/api/session");session.new_goals ||= [];
    $("period-label").textContent=`${session.period.type==="weekly"?"周报":"月报"} · ${session.period.start} — ${session.period.end}`;
    for(const dept of new Set(session.tasks.map(t=>t.department))) $("department").append(new Option(dept,dept));
    renderGroups();renderCards();renderNewGoals();
    $("message").textContent="已有信息可展开核对。每个问题都可以填写事实，或明确说明暂无法提供的原因。";
    if(!["draft","ready"].includes(session.status)) {$("message").textContent=session.status==="generated"?"本期报告已生成并归档。":"本期补充已提交，等待当前会话继续生成。";lockForm();}
  } catch(error) {$("message").textContent=`无法读取本期事项：${error.message}`;lockForm();}
}
for(const id of ["department","priority","completion"]) $(id).addEventListener("change",renderCards);
$("save").addEventListener("click",()=>persist(false));$("submit").addEventListener("click",()=>persist(true));
$("add-goal").addEventListener("click",()=>{session.new_goals.push({id:`G-${crypto.randomUUID().slice(0,8)}`,observation:{},confirmed:false});markDirty();renderNewGoals();renderCards();});
window.addEventListener("beforeunload",event=>{if(dirty){event.preventDefault();event.returnValue="";}});
init();
