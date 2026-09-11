---
blueprint_kind: security
blueprint_status: draft
owner: TBD-SECURITY-001
last_reviewed: 2026-09-10
---

# 安全与隐私

## 数据与风险

| Data | Classification | Key control | State |
|---|---|---|---|
| 手机号、设备/推送标识 | personal | 最小收集、加密、访问/删除流程 | pending |
| 训练计划、打卡 | personal; 敏感性需评估 | 学员/教练关系对象级授权 | pending |
| 打卡照片 | personal，可能包含高敏感内容 | 私有存储、短时授权访问、元数据清理 | pending |
| 审计/安全日志 | confidential | 脱敏、限权、保留策略 | pending |

公众 API、移动端、教练 Web、对象存储、短信/推送 SDK 和云平台是信任边界。服务端对角色与教练-学员关系授权；客户端隐藏不构成控制。验证码需频控、枚举防护和重放/过期验证。上传限制类型/大小/数量，随机对象键，恶意内容与图像处理策略待风险评审。

传输和托管存储加密；秘密在托管 secret store 中分权与轮换。SDK/依赖维护清单、用途、权限、网络行为、版本和供应商；CI 执行依赖、秘密和移动构建检查。审计记录教练查看敏感资料与计划变更，不写验证码或完整手机号。

## 大陆上线核实

上线主体、域名/服务备案、隐私告知/同意、敏感信息处理、未成年人、数据驻留/跨境、用户权利、第三方 SDK 披露、应用商店材料及健康内容边界必须由责任人依据届时官方来源核实。本草案不作法律结论。短信、推送、对象存储和分析供应商须作为处理方/子处理方评审并具备退出路径。

## 事件响应

指定检测、证据保全、分级、升级、用户/监管沟通和复盘负责人；未完成演练与联系表阻断生产。高风险路径至少包括验证码滥用、越权查看照片、签名链接泄露和第三方 SDK 异常传输。

## Open decisions

| TBD ID | Decision | Owner | Decision by | Blocked gate | State |
|---|---|---|---|---|---|
| TBD-SECURITY-001 | 确认数据分类/保留、授权、上传安全、SDK/供应商、合规与事件负责人 | security/compliance owner | 上线评审前 | production-ready | pending |
