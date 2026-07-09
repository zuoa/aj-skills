# Output Template

The final deliverable is **one markdown file**. Use this skeleton. Sections map 1:1 to the seven phases. Keep tables; evaluators scan them. Replace `[bracketed]` content. Omit Phase 6 only if the concept is trivial enough that risks/phasing add nothing (rare).

```markdown
# [Concept name]
## 可行性分析与结构化拆解

> 编制依据
> - 设想/方案来源：[concept doc name or description]
> - 对标框架：[framework name + issuing body + source/URL + doc number if any]
> - 方法论：[decomposition method used — default: V字模型（业务协同模型 + 数据共享模型双贯穿）]

---

## 一、对标对齐（Alignment mapping）

[2–3 sentences: how the concept relates to the framework strategically.]

### 对齐矩阵

| 框架维度 | 设想覆盖 | 数据来源 | 对齐度 | 缺口与建议 |
|---|---|---|---|---|
| [dim 1] | [coverage] | [source] | ★★★★★ / ★★★☆☆ / ☆☆☆☆☆ | [gap or "—"] |
| … | | | | |

### 关键结论
- 战略契合度：…
- 必须补齐的缺口：…
- 突出的对齐点（→ 亮点）：…

---

## 二、可行性深度分析（Feasibility）

### 2.1 技术可行性（按层/组件）
[per-layer table or prose with ★/◑/⚠]

### 2.2 组织/运营可行性
### 2.3 合规与伦理可行性  ← 命名具体法规 + 具体红线 + 去风险动作
### 2.4 经济/可持续性可行性

### 可行性总体结论
| 模块 | 评级 | 定性 |
|---|---|---|
| … | ★/◑/⚠ | … |

**关键（killer）约束**：[one sentence]。
**去风险动作**：[the specific design choice / reform item].

---

## 三、亮点提炼（Highlights）

> 按评审四维：政策契合 / 模式创新 / 技术先进性 / 成效可量化（+ 可复制性 + 合规引领）。

### 亮点1：[title] — [claim] · 证据：[proof]
### 亮点2：…
…

---

## 四、结构化拆解（V字模型 / adapted method）

### 4.x 业务协同模型（V字下行）
```
① 总任务
   │ 任务分解 ② …
   │ 业务梳理 ③ …
   │ 流程再造 ④ …
   │ 规则重构 ⑤ …
   ▼
```
### 4.y 数据共享模型（V字下行，并行）
```
① 数据需求识别
   │ 数据归集 ② …
   │ 数据治理 ③ …
   │ 数据共享 ④ …
   ▼
```
### 4.z 综合集成（V字上行）
```
基础设施 ▲ 数据/应用集成 ▲ 试点→推广 ▲ 评估→制度固化
```

> 非数字化改革语境：用框架原生的分解结构替换上面的 V，并在此注明所用的方法与两条轴。

---

## 五、四张清单（核心交付）

### 清单一　业务功能清单
| 编号 | 业务功能 | 所属层 | 功能描述 | 使用角色 | 触发条件 | 关联数据 |
|---|---|---|---|---|---|---|
| F1.1 | … | … | … | … | … | … |

**功能总数：N 项（…）**

### 清单二　数据依赖及共享清单
| 编号 | 数据实体 | 核心数据项 | 来源方 | 采集方式 | 共享方与用途 | 更新频率 | 敏感等级 | 合规要求 |
|---|---|---|---|---|---|---|---|---|
| D1 | … | … | … | … | … | … | H/M/L | … |

**数据共享机制要点**：[主数据主键 / 共享规则 / 跨主体通道 / 脱敏与开放]

### 清单三　基础设施依赖清单
| 层级 | 依赖项 | 用途·规格 | 建设方式 |
|---|---|---|---|
| 终端感知 / 网络 / 计算存储 / 平台·AI / 集成 / 移动·门户 / 安全合规 | … | … | … |

### 清单四　改革变革项清单
| 类别 | 编号 | 变革项 | 核心内容 | 突破的旧机制 |
|---|---|---|---|---|
| 制度重塑/流程再造/规则重构/机制创新/标准规范 | G1 | … | … | … |

**改革变革项总计：N 项（制度… + 流程… + 规则… + 机制… + 标准…）**

> 非数字化改革语境：按 references/decomposition-and-checklists.md 的适配表替换四张清单的轴，并在此注明。

---

## 六、风险与分期（Risks & phasing）

### 风险对策
| 风险 | 等级 | 对策 |
|---|---|---|

### 分期实施
| 阶段 | 周期 | 重点 | 目标 |
|---|---|---|---|

---

*本分析可作为深化设计、立项可研/初设、奖项申报材料的统一底稿。*
```

## Notes on producing it

- Write the file with the `Write` tool to a descriptive path in the working directory.
- Cite the framework's real source at the top (URL / doc number / issuing body). If a requirement couldn't be fully verified, say so inline.
- Keep tables tight; if a cell would be a paragraph, summarize and move detail to prose below.
- After writing, return a **short summary** to the user: gaps found, killer constraint, top highlights, list counts. Then offer 2–3 next steps (Word/PDF conversion, deepen a list into 可研/初设, design the indicator system). Offer only.
