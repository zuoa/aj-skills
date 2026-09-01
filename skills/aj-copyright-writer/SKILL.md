---
name: aj-copyright-writer
description: 编写和补正中国计算机软件著作权登记材料。用户要求生成或修改软著、软件著作权、源程序鉴别材料、操作手册、软件设计说明书、界面原型、代码文档、申请表信息，或提到“模板化程度较高”“独创性、代表性不足”等补正意见时必须使用。固定生成 10 个核心业务模块，但按软件类型选择自洽技术栈和代表性文档，排除通用脚手架与空壳代码，并在输出正式 DOCX 前执行内部独创性审计。
---

# AJ Copyright Writer

生成高质量、业务一致的软件著作权登记材料。格式合规只是底线；模块、源码、文档、界面和申请表必须共同呈现该软件的专有业务表达，不能只更换名称后复用同一套代码或文字骨架。

## 必读资源

- 全流程与目录约定：[references/workflow-contract.md](references/workflow-contract.md)
- 模块、源码和文档写作：[references/material-writing-rules.md](references/material-writing-rules.md)
- 登记材料硬规则：[references/software-registration-rules.md](references/software-registration-rules.md)
- 原型风格：[references/prototype-ui-style.md](references/prototype-ui-style.md)
- 选择操作手册时：[references/operation-manual-template.md](references/operation-manual-template.md)
- 选择软件设计说明书时：[references/software-design-template.md](references/software-design-template.md)
- 操作手册完成后：[references/operation-manual-humanizer.md](references/operation-manual-humanizer.md)

国家版权局 2025 年版权政策只可作为行业背景，不把它当作软件登记材料的操作规则。登记规则以《计算机软件著作权登记办法》和本技能的 `software-registration-rules.md` 为准。

`{baseDir}` 表示本 `SKILL.md` 所在目录。所有脚本均使用 `{baseDir}/scripts/...` 的绝对解析路径执行。

## 输入与模式

必需输入：`SOFTWARE_NAME`。

可选输入：

- `SOFTWARE_VERSION`：默认 `V1.0`。
- 输出目录：默认 `copyright-materials/{software_slug}-{YYYYMMDD-HHMM}/`。
- `MODE`：`normal` 或 `correction`。只有用户提供补正通知或明确要求补正时才自动选择 `correction`；首次申请即使提供现有代码或文档仍使用 `normal`。
- 现有代码、文档、截图、补正通知和历史材料目录。
- 实际技术栈。用户未指定时，根据软件类型自动选择一套自洽技术栈。
- 文档类型：`operation-manual` 或 `design-specification`。
- 原型模式：默认 HTML；用户明确要求图片模型时才使用 image 模式。

补正模式始终创建新的输出目录，不覆盖原材料。先分析旧材料的问题，再重新选择业务内容；禁止只改变量名、同义替换或打乱段落顺序。

## 正式输出

```text
01.spec/spec.md
02.modules/01.md ... 10.md
03.prototype.style/selection.md
03.prototype.html/*.html 或 03.prototype.prompt/*.md
04.prototype/batch.json、*.jpg
05.code/01-模块名称.txt ... 10-模块名称.txt
06.document/${SOFTWARE_NAME}_操作手册.md/.docx
或 06.document/${SOFTWARE_NAME}_软件设计说明书.md/.docx
07.code.full/${SOFTWARE_NAME}_代码.docx
08.application-info/${SOFTWARE_NAME}_软著申请表信息.txt
09.originality-audit/source-manifest.json
09.originality-audit/originality-report.json
09.originality-audit/originality-report.md
```

`09.originality-audit` 是内部质量检查目录，不得把其中的文字复制到 `01`—`08` 正式材料。正式材料不得出现“本文为草案”“AI 生成”“模板化材料”“基于推断扩展”“扩展设定”“独创性审计结果”等生成过程说明；软件名称和真实业务术语中的 `AI`、`合同模板` 等必须正常保留。

## 工作流

### 1. 调研与业务锚点

1. 使用软件名称检索官网、产品资料、行业规范和权威业务资料。
2. 提炼软件专有的业务对象、字段、状态、规则、计算口径、异常场景、角色和行业术语。
3. 把这些内容写成正式的软件规格说明，包括定位、用户、场景、业务流程、架构、数据对象、功能和非功能要求。
4. 不在正式规格中写资料来源分级、假设声明或生成说明。

业务锚点是后续一致性的唯一口径。代码、界面、文档和申请表不得回退到与任何系统都适用的通用表述。

### 2. 固定生成 10 个核心模块

- 恰好生成 `02.modules/01.md` 到 `10.md`，每个模块包含 3—5 个功能点。
- 至少 8 个模块必须是行业或业务核心模块；登录、用户、角色、权限、日志、字典、设置、帮助等通用模块合计不得超过 2 个。
- 模块名、功能名、字段、状态、业务规则和异常分支必须使用本软件的行业语义。
- 每个模块在“模块定位”中说明它如何体现本软件的代表性能力，但不要使用夸张宣传或审查话术。
- 禁止使用 `数据管理 / 信息维护 / 统计分析` 等泛化名称占据核心模块。

生成后运行：

```bash
python3 {baseDir}/scripts/validate_outputs.py \
  --spec-md 01.spec/spec.md \
  --module-dir 02.modules
```

### 3. 选择代表性文档

按以下优先级选择：

1. 用户明确指定的文档类型。
2. 收到“文档模板化程度较高”补正意见时，默认选择软件设计说明书；只有真实界面和操作闭环明显更具代表性时才选择操作手册。
3. 交互、审批、调度、运营类软件选择操作手册。
4. 算法、后台服务、数据处理、设备接入、协议解析类软件选择软件设计说明书。

在内部记录选择结果和理由，但正式文档只呈现软件内容。

选择后设置内部变量：操作手册使用 `DOCUMENT_TYPE=operation-manual`、`DOCUMENT_BASENAME=${SOFTWARE_NAME}_操作手册`；软件设计说明书使用 `DOCUMENT_TYPE=design-specification`、`DOCUMENT_BASENAME=${SOFTWARE_NAME}_软件设计说明书`。同时用一句具体理由设置 `DOCUMENT_SELECTION_REASON`，该理由只写入内部审计报告。

### 4. 生成原型与截图

需要界面材料时，先读 `prototype-ui-style.md`，推荐行业匹配风格并让用户确认。生成 `selection.md` 后再写 HTML 或图片 prompt。

HTML 必须自包含，使用中文业务字段、真实状态和合理 mock 数据，固定 1920×1080，不依赖 CDN、远程字体或接口。页面不得出现版权归属、开发公司、技术支持、出品方或承建单位署名。

操作手册至少生成 10 个模块首页，并为 40%—60% 的复杂功能点生成独立截图。只有软件确有账号登录流程时才生成 `00-login`；无登录流程时使用真实入口、首页或任务起始页，并在截图与验证命令中使用 `--no-login`。软件设计说明书只生成能证明系统结构、核心流程或关键处理结果的代表性界面，不为凑数量制作空白后台页面。

HTML 模式：

```bash
python3 {baseDir}/scripts/screenshot_html_prototypes.py \
  --html-dir 03.prototype.html \
  --output-dir 04.prototype \
  --module-dir 02.modules \
  --batch-file 04.prototype/batch.json \
  --viewport 1920x1080
```

软件没有登录流程时，在截图脚本以及后续 `validate_outputs.py` 命令中追加 `--no-login`。

### 5. 生成代表性源程序

#### 技术栈

- 优先采用用户真实技术栈；否则按软件类型选择一套自洽方案。
- 技术栈必须贯穿规格、代码、设计文档和申请表。
- 10 个代码文件按架构职责和业务模块组织，不要求每个文件同时包含前端和后端。
- 源码必须语法连贯、类型和接口一致，不写“仅作示例”式伪代码。

#### 入选内容

优先包含领域服务、状态流转、规则判定、计算或匹配算法、数据转换、协议解析、复杂校验、权限边界、异常恢复和审计轨迹。

排除：

- 只有 import、package、using 或依赖声明的文件；
- 环境配置、构建配置、启动胶水和纯路由注册；
- 纯 getter/setter、无业务行为的 DTO 或实体；
- 空方法、空接口、空组件、TODO 和占位页面；
- 自动生成客户端、第三方库和框架源码；
- 仅替换类名或字段名的重复 CRUD；
- 无业务含义的重复注释。

不要从入选业务文件中机械删除必要 import。应排除低价值文件，同时保持入选源码的结构完整和可读性。

#### 行数与顺序

- `05.code` 恰好包含 10 个 `编号-模块名称.txt` 文件。
- 不设置单文件统一行数；复杂模块自然包含更多代码。
- 10 个文件合计至少 3000 个非空源码行，以满足 60 页、每页 50 行。
- 注释只解释业务口径、状态转换、边界和非显而易见逻辑，不设机械注释率目标。
- `05.code` 可以保留正常的源码空行以维持可读性；统计和代码 DOCX 组版时忽略空行。源码不得包含 `copyright` 字样。

### 6. 编写正式鉴别文档

操作手册必须基于真实任务组织章节，针对任务办理、审核闭环、监控处置、分析查询、批量导入和规则配置采用不同写法，不让所有功能重复同一种段落骨架。所有按钮、字段、状态和提示语必须能在对应界面找到。

软件设计说明书必须说明领域模型、状态转换、核心处理流程、算法输入输出、接口关系、校验与异常策略，并明确这些内容对应的代码模块。不得把十个模块机械扩写成十段相同结构。

正式 Markdown 直接写入 `06.document`，不保存带 `.draft` 名称的正式产物。转换 Word：

```bash
python3 {baseDir}/scripts/markdown_to_docx.py \
  --input "06.document/${DOCUMENT_BASENAME}.md" \
  --output "06.document/${DOCUMENT_BASENAME}.docx" \
  --template "${DOCUMENT_TEMPLATE:-}"
```

### 7. 执行内部独创性审计

在生成正式代码 DOCX 前运行：

```bash
python3 {baseDir}/scripts/audit_originality.py \
  --code-dir 05.code \
  --module-dir 02.modules \
  --document "06.document/${DOCUMENT_BASENAME}.md" \
  --document-type "${DOCUMENT_TYPE}" \
  --document-selection-reason "${DOCUMENT_SELECTION_REASON}" \
  --output-dir 09.originality-audit
```

用户提供历史材料时追加 `--comparison-corpus /path/to/history`。

审计阻断以下问题：空实现、明确占位代码、低价值文件、过量精确重复代码块、超过两个通用模块、多组模板化文档段落、文档漏掉核心模块，以及与历史材料高度相似。结构相似度等不确定指标只给警告。审计阈值是内部质量启发式，不是登记机关公开标准。

若审计失败，回到模块、代码或文档步骤实质性重写；不得使用 `--allow-high-risk` 生成正式交付。

### 8. 生成 60 页代码文档

```bash
python3 {baseDir}/scripts/build_code_docx.py \
  --code-dir 05.code \
  --source-manifest 09.originality-audit/source-manifest.json \
  --originality-report 09.originality-audit/originality-report.json \
  --output "07.code.full/${SOFTWARE_NAME}_代码.docx" \
  --software-name "${SOFTWARE_NAME}" \
  --software-version "${SOFTWARE_VERSION:-V1.0}"
```

代码文档必须是 60 个代码页，每页 50 行，宋体小五、左对齐、单倍行距。页眉名称和版本与申请表一致，右上角为页码。超过 3000 行时按普通交存口径取连续源码流的前 1500 行和后 1500 行，最后一页为程序结束部分。

### 9. 生成申请表信息

生成 `08.application-info/${SOFTWARE_NAME}_软著申请表信息.txt`。硬件环境、操作系统、开发工具、运行平台、支撑环境、开发目的、行业各不超过 50 字符；主要功能不超过 200 字；技术特点不超过 100 字。

编程语言和版本从 `source-manifest.json` 读取，源程序量使用 10 个代码文件的非空行总数。软件类型从 `APP、游戏软件、教育软件、金融软件、医疗软件、地理信息软件、云计算软件、信息安全软件、大数据软件、人工智能软件、VR软件、5G软件、小程序、物联网软件、智慧城市软件` 中选一个。

### 10. 最终验证

```bash
python3 {baseDir}/scripts/validate_outputs.py \
  --code-dir 05.code \
  --source-manifest 09.originality-audit/source-manifest.json \
  --originality-report 09.originality-audit/originality-report.json \
  --document-md "06.document/${DOCUMENT_BASENAME}.md" \
  --document-docx "06.document/${DOCUMENT_BASENAME}.docx" \
  --code-docx "07.code.full/${SOFTWARE_NAME}_代码.docx" \
  --application-info-txt "08.application-info/${SOFTWARE_NAME}_软著申请表信息.txt" \
  --software-name "${SOFTWARE_NAME}" \
  --software-version "${SOFTWARE_VERSION:-V1.0}"
```

## 交付检查

- 是否恰好有 10 个模块和 10 个编号代码文件，且至少 8 个是业务核心模块。
- 技术栈是否自洽，是否清除了 import-only、配置、访问器、空壳、生成代码、第三方代码和重复 CRUD。
- 正式文档类型是否适合软件，是否避免重复句式并覆盖全部核心模块。
- 文档、截图、代码和申请表中的名称、字段、状态、技术栈和版本是否一致。
- 内部审计是否为 `pass`，源码指纹是否仍与审计时一致。
- 代码 DOCX 是否为 60 页、每页 50 行，页眉和页码是否正确。
- 正式材料是否没有草案标记、AI 生成、模板化材料、基于推断扩展和内部审计结果等过程说明，同时保留软件名称和真实业务术语。

最终回复只列输出目录、文档类型、核心文件、所用技术栈、模板使用情况、验证结果和未完成项，不把整份代码或文档粘贴到聊天中。
