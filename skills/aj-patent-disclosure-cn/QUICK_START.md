# 快速开始

## 1. 直接调用

信息较完整时：

```text
使用 aj-patent-disclosure-cn，根据下面方案生成中国发明专利技术交底书草案。
请区分已确认事实、推断和待确认项；不要编造检索结果或实验数据。

技术场景：...
现有方案和不足：...
输入/处理对象：...
核心步骤或模块关系：...
输出：...
区别特征：...
技术效果及证据：...
希望保护的主题：...
```

信息很少时可以只给现有想法。skill 会优先询问 3–5 个影响技术链和保护范围的问题，不会先要求安装环境。

有项目目录或材料时：

```text
请扫描这个项目中的设计文档、核心代码、Word/PPT 和测试记录，先建立“技术事实—来源定位—版本—拟保护特征”证据清单，再挖掘专利点。忽略第三方依赖、生成文件和无关资源，不要读取或回显密钥。
```

## 2. 只做某个环节

```text
只做专利点挖掘，先不要写交底书。
```

```text
请联网检索与本方案相关的现有专利：先形成必要技术特征表，查找最接近现有技术，逐项对比并提取区别特征；再围绕“区别特征 + 功能关系 + 技术效果”反向检索，筛选有事实支撑的初步创新点。每个结论都给出公开号、日期、证据位置和来源链接；没有实际检索时明确说明，不要编造结果。
```

```text
审校这份交底书的充分公开、支持性、术语一致性和AI方案披露风险。
```

```text
只制定检索式和特征对照表；没有实际检索能力时不要给专利号。
```

```text
基于已确认正文规划附图，不改动技术内容。
```

```text
请解读这份专利 PDF：核对文本版本，建立权利要求树，逐项写清从属权相对父权新增了什么，并把独立权特征映射到说明书段落和附图。只拿到摘要时明确证据不足，不要把摘要当全文。
```

```text
在上一版交底书上补充这份测试报告。保留旧稿，另存新版本；同步检查技术效果、实施例、支撑矩阵、附图和检索结论，并生成修订记录。
```

## 3. 转换 Office 材料

```bash
python3 scripts/office_to_markdown.py \
  docs/design.docx docs/review.pptx \
  --output-dir outputs/materials \
  --manifest outputs/materials/office_manifest.json
```

转换稿用于内部扫描和证据定位，不保证原版式还原。

## 4. 结构化输入校验

```bash
python3 scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json
```

正式导出前：

```bash
python3 scripts/validate_disclosure.py \
  --input examples/disclosure_input.sample.json \
  --final
```

## 5. 生成 Markdown + Word

依赖可用时直接执行：

```bash
python3 scripts/generate_docx.py \
  --input examples/disclosure_input.sample.json \
  --output outputs/交底书_示例_v1.0.docx \
  --with-markdown
```

只有出现缺少依赖的错误时，才初始化本地环境：

```bash
bash scripts/setup_env.sh
./.venv/bin/python scripts/generate_docx.py \
  --input examples/disclosure_input.sample.json \
  --output outputs/交底书_示例_v1.0.docx \
  --with-markdown
```

## 6. 修订留痕

```bash
python3 scripts/revision_log.py \
  --case-dir outputs/某案件 \
  --kind supplement \
  --base outputs/某案件/交底书_v1.md \
  --artifact outputs/某案件/交底书_v2.md \
  --artifact outputs/某案件/交底书_v2.docx \
  --changed-section "实施例1" \
  --summary "补充异常回退路径并同步附图"
```

## 7. 关键原则

- 专利点来自已披露技术因果链，不靠堆叠流行技术名词；
- 研发建议与已经实现的发明事实分开；
- 量化效果必须有测试条件、基线或来源；
- 新颖性不按多篇文献拼接，也不按文本相似度判断；
- 区别特征不直接等于创新点，必须经过相似专利对比、反向检索和技术效果验证；
- 项目代码、测试和 Office 材料中的关键事实应保留版本与来源定位；
- 已有专利解读必须区分全文、部分全文、仅摘要和待核验；
- 修改已有交底书默认保留旧稿并传播检查所有受影响章节；
- 脱敏不能删除使方案可实施或支撑保护范围的关键技术细节；
- AI/算法方案要披露模型/算法与具体场景的内在关系；
- DOCX、附图和检索不是每次调用都必须执行，按任务需要生成。
