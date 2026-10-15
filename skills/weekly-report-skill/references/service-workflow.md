# 补充服务与恢复流程

## 命令

均通过 `scripts/report_workflow.py` 调用；路径含空格时使用 shell 引号。

| 命令 | 参数 | 结果 |
|---|---|---|
| `prepare` | `--workdir`、`--input` | 校验提取数据，继承目标，生成问题；已有会话拒绝覆盖 |
| `serve` | `--workdir`、`--period`、可选 `--port`、`--no-browser` | 启动本地界面；默认端口 0 自动分配，并尝试弹出浏览器 |
| `status` | `--workdir`、`--period` | 查看状态、活跃问题数、未回答项及文件位置 |
| `validate` | `--workdir`、`--period` | 检查所有适用问题，未完成时返回非零退出码 |
| `merge` | `--workdir`、`--period` | 校验已提交答案，保存台账、分析、快照和确认记录 |
| `finalize` | `--workdir`、`--period`、`--report` | 保存最终报告副本和哈希，标记已生成 |

业务调用时不能使用 `--no-browser` 省略可视化；该选项用于自动化测试或已明确手动打开链接的环境。

正常执行：prepare → 若 draft 则 serve → 等待 submitted → merge → agent 按模板写报告 → finalize → 停止本次服务。

`status=ready` 的完整材料可跳过 serve。脚本不调用模型、不发送外部消息、不发布报告。页面文案“提交并继续生成”表示通知当前 agent；服务本身不生成业务正文。

## 服务 API

仅监听 `127.0.0.1`，不提供任意文件读取或路径提交。所有 `/api/*` 请求需要启动链接片段中的令牌作为 `X-Session-Token`；令牌不放在查询参数或日志中。写接口限制为同源 JSON、最大 2 MB。

- `GET /api/session`：读取问题、已保存草稿、当前状态和 revision。
- `POST /api/draft`：保存部分答案及新增目标，返回新 revision。
- `POST /api/submit`：逐项校验后原子保存，返回 submitted。缺少回答返回 HTTP 422 和 `{task_id, field, message}`，页面定位错误；未通过提交时不会更新磁盘草稿，页面仍保留填写，用户可点击保存草稿。

两项写请求都传 `{revision, answers, new_goals}`；旧 revision、已提交修改或无效格式被拒绝。页面用文本节点呈现材料，避免把文档文字当 HTML 执行。

## 等待与恢复

- 使用工具支持的持久进程启动 serve，保存进程句柄；每 5–15 秒查看 status，单次阻塞不超过 30 秒，持续等待期间正常给用户进度说明。
- 浏览器自动打开失败：输出的完整链接仍可访问。GUI 或监听权限受限制时按宿主权限流程请求运行；不要把失败解释为资料已确认。
- 等待较久：提醒用户可保存草稿。不得因超时把问题标成已确认或默认未知。
- 新一轮调用先读取本期 session。draft 重启服务并继续填写；submitted/ready 直接 merge；merged 继续写报告并 finalize；generated 返回现有报告或按要求建立修订。
- 台账 revision 冲突：另一个周期已更新目标，建立新修订周期，读取最新基线后确认；不要强制覆盖。
- merge 成功后重复调用不会再增加变更历史；台账写入后会话状态写入前发生崩溃时，可根据同一次提交和 snapshot 恢复。
- 若该工作目录中已有未完成的 merged 周期，先完成其报告，再开始其他周期，避免多个周期交叉提交。
- 结束时只终止本次服务进程；Ctrl+C 会清理 runtime.json。异常结束遗留 runtime 时重新启动会覆盖链接，不影响草稿。

## 开发验证

```bash
python3 -m unittest discover -s <skill-dir>/tests -v
python3 <skill-dir>/scripts/report_workflow.py --help
```

用临时业务目录进行测试，不能把测试确认当成真实用户确认。浏览器检查逐项问题、条件字段、保存刷新、未知原因必填、非法提交、成功提交及窄屏布局。单元测试验证台账和 HTTP 行为，业务写作质量通过配套 eval prompts 检查。
