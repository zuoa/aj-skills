# Decomposition Method & Checklists

Used in Phases 4 & 5. Covers the default V字模型 method, the four-list schemas, and how to adapt both when the framework is **not** digital reform.

## Table of contents
1. Default: the V字模型 (digital reform / 课题申报 context)
2. Threading the two models through every phase
3. The four checklists: column schemas
4. Adaptation rules (non-digital-reform frameworks)

---

## 1. Default — the V字模型

The V字模型 (used in 浙江 数字化改革) is: **self-top-down decomposition (V-down) + self-bottom-up integration (V-up)**, with the **业务协同模型** and **数据共享模型** running in parallel as the twin spines through the whole V.

### V-down (自上而下分解) — build the two models

**业务协同模型 spine (business collaboration):**
```
① 总任务 (the whole thing the concept is trying to do)
   │  任务分解  ② split into sub-tasks (识别 / 预警 / 诊断 / 方案 / 执行 / 优化 …)
   │  业务梳理  ③ for each sub-task, define every party's responsibility boundary & handoff
   │  流程再造  ④ redesign the closed loop end-to-end (trigger → steps → SLA → exit criteria)
   │  规则重构  ⑤ the decision rules (grading, escalation, routing, case-open, case-close)
   ▼  → feeds 清单一 (业务功能) + 清单四 (改革变革)
```

**数据共享模型 spine (data sharing) — runs in parallel:**
```
① 数据需求识别  what data each sub-task needs, who produces, who consumes
   │  数据归集    ② gather from all sources (devices / apps / partner APIs / manual)
   │  数据治理    ③ standardize data elements, dedup, align by time/space/master-key
   │  数据共享    ④ sharing scope, sharing method (API/authorized), sharing rules (min-necessary + consent)
   ▼  → feeds 清单二 (数据依赖及共享)
```

### V-up (自下而上集成)

```
基础设施 (cloud/network/edge/IoT/AI)        ← feeds 清单三 (基础设施)
   ▲  数据底座集成 → 应用模块集成 → 统一门户
   ▲  试点 → 迭代 → 区域推广
   ▲  多维效能评估 → 改革制度成果固化         ← feeds 清单四 (改革变革) + 成效评估
```

Render the V as two ASCII trees (one per spine) so the reader sees the two models literally threaded top-to-bottom. That visual is itself a deliverable artifact evaluators like.

---

## 2. Threading the two models through every phase

The common failure mode is to mention 业务协同 and 数据共享 once in a section and forget them elsewhere. Thread them instead:

| Phase | Business-collaboration question | Data-sharing question |
|---|---|---|
| Alignment | which framework requirements need cross-party workflow? | which need cross-source data? |
| Feasibility | is the cross-party cooperation sustainable? | is the cross-source sharing compliant/feasible? |
| Highlights | what new closed-loop/collaboration is novel? | what new data pathway/asset is created? |
| Decomposition | V-down business spine | V-down data spine |
| Checklists | 业务功能清单 + 改革变革项 | 数据依赖及共享清单 |
| Risks/phasing | cooperation incentive mechanism | data governance & cold-start |

If you can't fill a cell, the concept has a hole — surface it.

---

## 3. The four checklists (default schemas)

### 清单一 — 业务功能清单 (business functions)
| 编号 | 业务功能 | 所属层 | 功能描述 | 使用角色 | 触发条件 | 关联数据 |
Columns: id (e.g., F1.1, layer-prefix + number) · name · layer · description · role · trigger · related-data. Group by layer; give a total count at the end.

### 清单二 — 数据依赖及共享清单 (data dependency & sharing)
| 编号 | 数据实体 | 核心数据项 | 来源方 | 采集方式 | 共享方与用途 | 更新频率 | 敏感等级 | 合规要求 |
Columns: id · entity (align entities to the framework's dimensions where possible) · core items · source party · collection method · sharing parties & purpose · frequency · sensitivity (H/M/L) · compliance. End with a short **数据共享机制要点** (master-key, sharing rules, cross-party channels, de-identification/open rules).

### 清单三 — 基础设施依赖清单 (infrastructure)
A table grouped by layer, no rigid columns: **层级 / 依赖项 / 用途·规格 / 建设方式**. Standard layers: 终端感知 / 网络 / 计算存储 / 平台·AI / 集成 / 移动·门户 / 安全合规. Always include the **security/compliance layer** (等保/加密/脱敏/隐私计算/IAM/审计/灾备).

### 清单四 — 改革变革项清单 (reform & transformation)
| 类别 | 编号 | 变革项 | 核心内容 | 突破的旧机制 |
Categories: 制度重塑 / 流程再造 / 规则重构 / 机制创新 / 标准规范. Each row must state what old mechanism it breaks — that "breaks from" column is the proof of reform-gold-content. End with a category count.

---

## 4. Adaptation rules — when the framework is NOT digital reform

The V字模型 and these exact four lists are the right default for **digital reform / 课题申报 / 数字政府 / 政企信息化立项**. When the framework is different, adapt — but keep the *shape* (two complementary axes + standardized lists):

| Framework type | Decomposition method (replace V字模型) | Checklist axes (replace the four) |
|---|---|---|
| **Industry / national standard (GB, 行业规范)** | Decompose by the standard's clause/requirement structure; one process-axis (how to satisfy) + one evidence-axis (how to prove conformity) | 合规功能清单 / 证据·数据清单 / 工具·测试依赖清单 / 整改·制度清单 |
| **Technical spec / RFC / 协议** | Decompose by spec sections (requirements, interfaces, data models, conformance) | 接口功能清单 / 数据模型·字段清单 / 依赖组件清单 / 测试·一致性清单 |
| **Research methodology / 课题研究框架** | Decompose by methodology stages (problem → method → data → analysis → findings) | 研究任务清单 / 数据·资料清单 / 方法·工具依赖清单 / 成果·产出清单 |
| **Compliance regime (ISO 27001, 等保, GDPR)** | Decompose by control domains; process-axis (control activity) + evidence-axis (audit evidence) | 控制措施清单 / 证据·记录清单 / 技术·工具依赖清单 / 制度·流程清单 |
| **Corporate strategy / 业务规划** | Decompose by strategic objectives → initiatives → capabilities | 业务能力清单 / 数据·指标清单 / 资源·系统依赖清单 / 组织·机制变革清单 |

The invariant across all cases: **two complementary axes (one process/workflow, one data/information), threaded through every phase, landing in standardized tables.** If you're unsure which adaptation fits, default to the V字模型 + four lists and note the deviation.
