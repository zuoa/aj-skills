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

## 2. 只做某个环节

```text
只做专利点挖掘，先不要写交底书。
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

## 3. 结构化输入校验

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

## 4. 生成 Word

依赖可用时直接执行：

```bash
python3 scripts/generate_docx.py \
  --input examples/disclosure_input.sample.json \
  --output outputs/交底书_示例_v1.0.docx \
  --word-only
```

只有出现缺少依赖的错误时，才初始化本地环境：

```bash
bash scripts/setup_env.sh
./.venv/bin/python scripts/generate_docx.py \
  --input examples/disclosure_input.sample.json \
  --output outputs/交底书_示例_v1.0.docx \
  --word-only
```

## 5. 关键原则

- 专利点来自已披露技术因果链，不靠堆叠流行技术名词；
- 研发建议与已经实现的发明事实分开；
- 量化效果必须有测试条件、基线或来源；
- 新颖性不按多篇文献拼接，也不按文本相似度判断；
- AI/算法方案要披露模型/算法与具体场景的内在关系；
- DOCX、附图和检索不是每次调用都必须执行，按任务需要生成。
