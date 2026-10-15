# 模板入口（兼容原引用）

周报与月报已拆分，按报告类型读取：

- [周报模板](weekly-template.md)：本周进展、近期节点、纠偏动作和下周承诺。
- [月报模板](monthly-template.md)：月度目标、指标趋势、重点交付和下月安排。

人工补充与确认记录由 `scripts/report_workflow.py merge` 生成；详细规则见 [数据契约](data-contract.md) 与 [服务操作](service-workflow.md)。所有模板均自包含，不依赖本机外部文档。
