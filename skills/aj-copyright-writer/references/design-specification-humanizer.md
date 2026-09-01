# Software Design Specification Language Pass

Use this pass after the technical content is complete and before converting the Markdown to DOCX. Its purpose is to make the specification read like a document written by the project's technical staff. Keep field names, states, rules, interfaces and implementation symbols unchanged.

## Working tone

Write down what the software actually does. Start paragraphs with the business object, the triggering event or the responsible component. Follow with the condition, action and result. Stop when the mechanism is clear.

Project engineers usually write sentences such as:

```text
标签绑定前，系统先检查 RFID 号是否已关联其他个体。已关联的标签不允许重复绑定，并返回原个体编号供操作人核对。

设备离线期间的读数先保存在本地队列。连接恢复后按采集时间补传；服务端以设备号、采集时间和消息序号去重。
```

The writing does not need a conclusion after every paragraph. A paragraph may be two sentences if two sentences are enough.

## Remove stock language

Delete sentences that only announce importance, completeness or benefit. These phrases are usually a sign that the paragraph lacks a concrete mechanism:

- `本系统旨在……`、`本系统致力于……`、`围绕……构建……`；
- `全面提升`、`有效保障`、`显著提高`、`赋能`、`打造`；
- `形成完整闭环`、`实现全流程管理`、`提供有力支撑`；
- `确保系统高效、稳定、安全运行`、`具备良好的可扩展性`；
- `不仅……而且……`、`此外`、`从而`、`值得注意的是`；
- `为后续……奠定基础`、`为……提供保障`。

If a phrase carries a real claim, replace it with the observable rule or result. Do not swap it for a synonym.

## Rewrite patterns

### Abstract opening

Before:

```text
本系统围绕种鹅全生命周期管理需求，构建了完善的个体档案与 RFID 身份管理体系，有效保障数据的准确性和可追溯性。
```

After:

```text
每只种鹅使用一个个体编号。RFID 标签绑定后，采精、免疫、称重和转群记录都按该编号归档。更换标签时保留旧标签号和更换时间，历史记录不随标签变更。
```

### Empty architecture claim

Before:

```text
系统采用分层架构，各层职责清晰，具有良好的可维护性和扩展性。
```

After:

```text
接入服务只处理 RFID 读卡器和称重设备上报的原始数据。个体档案服务完成身份匹配和业务校验，通过后再写入档案库。设备数据格式变化时，只调整接入服务的解析器。
```

### Decorative reliability statement

Before:

```text
通过完善的异常处理和重试机制，确保业务处理的稳定性与可靠性。
```

After:

```text
写库超时时，本次消息不确认消费。消息队列最多重投 3 次；仍失败的消息转入异常队列，保留原始报文和最后一次错误信息。
```

Only use a number such as `3 次` when it is present in the specification, configuration or source program.

## Paragraph-level checks

- More than two adjacent paragraphs begin with `本系统`, `系统通过` or `通过……实现`: rewrite the openings.
- A paragraph contains no field, state, event, role, rule, component or result specific to the software: delete it or replace it with a concrete design statement.
- Three consecutive sentences have the same length and grammar: combine one or shorten one.
- A subsection ends with a general benefit statement: delete the ending.
- The same adjective appears repeatedly (`完整`, `高效`, `灵活`, `稳定`, `智能`): replace the claim with evidence.
- A list contains three abstract nouns but no decision or result: rewrite it as prose or a real rule table.

## Final read

Read only the body paragraphs once, without headings. They should sound like someone explaining the actual system to a colleague who will maintain it. If a paragraph could be moved to another software design specification unchanged, it is not finished.
