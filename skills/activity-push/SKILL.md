---
name: activity-push
description: Extracts activity information from WeChat article feeds, lets the model judge whether each article is truly an activity by reading the article semantics, writes raw/activity/structured JSON files, renders reviewable Markdown plus push-ready text, and sends updates to WeCom internal groups via webhook robots. Use this skill whenever the user mentions 公众号 feeds, 活动提取, 活动报名信息, 企业微信群推送, webhook 推送, feed-to-activity workflows, or wants a repeatable bash/curl pipeline that reads feeds.md and emits raw.json / activity.json / activity-structured.json / activity-structured.md / activity-push.txt.
---

# Activity Push Skill

用于从公众号文章源中筛选活动类文章，提取结构化活动信息，并通过企业微信群机器人 Webhook 推送到内部群。

这个 skill 适合以下任务：
- "根据 feeds.md 拉取最近 24 小时公众号文章并筛活动"
- "把活动文章提取成结构化 JSON"
- "把活动信息整理成适合群发送的内容"
- "通过 webhook 推送到企业微信内部群"

## Why this skill

参考 Claude 的 skill 最佳实践，这个 skill 将工作拆成两层：
- `SKILL.md` 负责触发条件、判断标准、步骤、质量要求和异常处理
- 所有实际抓取与推送动作都用 bash + `curl` + `jq` 执行
- "这是不是活动"由模型阅读文章后做语义判断，不用关键字脚本筛选
- 内部群推送使用 webhook 机器人，简单直接
- 复杂细节下沉到脚本和参考文档
- 地址坐标补全走高德地理编码 CLI

这样做的好处是：
- 避免把"活动判断"硬编码成脆弱关键字规则
- 保持执行动作可审计，所有请求都能落回 bash 和 `curl`
- 输出路径和文件格式稳定
- 区分"审阅用 Markdown"和"API 发送用纯文本"，避免消息体格式不兼容
- 用户以后只要给 `feeds.md`、`.env` 和执行目录，就能复用整条链路

## Compatibility

默认依赖这些命令：
- `bash`
- `curl`
- `jq`
- `date`
- `awk`
- `sed`

如果缺少 `jq`，应先明确告诉用户当前环境不满足 skill 依赖，不要改用 Python 兜底。

复杂推送逻辑使用：
- [`fetch_recent_feeds.sh`](/Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/fetch_recent_feeds.sh) - 拉取 feed
- `curl` - webhook 推送

可选工具：
- [`amap_geocode_wgs84.py`](/Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/amap_geocode_wgs84.py) - 地理编码
- [`render_activity_image.py`](/Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/render_activity_image.py) - 渲染图片

复杂 API 说明见：
- [`wecom-group-types-guide.md`](/Users/yujian/Code/py/aj-skills/skills/activity-push/references/wecom-group-types-guide.md) - 群类型与 API 支持完整说明

使用规则：
- `SKILL.md` 先给出主流程
- 只有在调试 webhook 推送问题时，才去读 `references/wecom-group-types-guide.md`

## Required Inputs

执行前确认以下输入存在：
- 执行目录 `EXEC_DIR`，默认使用当前工作目录
- `~/.aj-skills/.env`
- `feeds.md`

`~/.aj-skills/.env` 建议包含这些变量：

```bash
MP_API_HOST=...
MP_API_KEY=...
AMAP_WEB_SERVICE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
WE_COM_WEBHOOK_KEYS=2449ebfdd2b2a1f20d88f797e3627d8fc6
```

其中：
- `MP_API_HOST`：必填
- `MP_API_KEY`：可选；feed 接口需要鉴权时再提供
- `AMAP_WEB_SERVICE_KEY`：可选；需要把活动地址补全为坐标时提供
- `WE_COM_WEBHOOK_KEYS`：可选；需要执行 webhook 推送时提供。支持多群，逗号分隔

`feeds.md` 约定：
- 每行一个公众号
- 第一列是公众号 `MP_ID`
- 后续内容视为公众号名称
- 空行和 `#` 注释行会被忽略
- 若 `MP_ID` 末尾误带英文逗号，脚本会自动清理
- 若同一个 `MP_ID` 重复出现，脚本只按第一次出现处理

示例：

```text
gh_1234567890 科技早知道
gh_abcdef123456 AI 产品观察
```

## Default Workflow

按下面顺序执行，不要跳步：

### 1. 预检环境

```bash
EXEC_DIR="${EXEC_DIR:-$PWD}"
ENV_FILE="${HOME}/.aj-skills/.env"
FEEDS_FILE="${EXEC_DIR}/feeds.md"
TODAY="$(date +%Y%m%d)"
OUT_DIR="${EXEC_DIR}/activity-push/${TODAY}"

test -f "${ENV_FILE}" || { echo "缺少 ${ENV_FILE}"; exit 1; }
test -f "${FEEDS_FILE}" || { echo "缺少 ${FEEDS_FILE}"; exit 1; }
command -v curl >/dev/null || { echo "缺少 curl"; exit 1; }
command -v jq >/dev/null || { echo "缺少 jq"; exit 1; }

set -a
source "${ENV_FILE}"
set +a

test -n "${MP_API_HOST}" || { echo "缺少 MP_API_HOST"; exit 1; }

mkdir -p "${OUT_DIR}"
```

检查项：
- `~/.aj-skills/.env` 是否存在
- `MP_API_HOST` 是否存在
- `MP_API_KEY` 是否存在取决于 feed 接口是否需要鉴权
- `WE_COM_WEBHOOK_KEYS` 只有在需要执行第 6 步推送时才检查
- `feeds.md` 是否存在且至少包含一个公众号

注意：
- 不要在回复里泄露完整密钥
- 只显示 secret 的掩码或目标群数量

### 2. 拉取 feed 并生成 `raw.json`

```bash
FETCH_ARGS=(
  --feeds-file "${FEEDS_FILE}"
  --output-file "${OUT_DIR}/raw.json"
  --api-host "${MP_API_HOST}"
  --hours 24
)

if [ -n "${MP_API_KEY:-}" ]; then
  FETCH_ARGS+=(--api-key "${MP_API_KEY}")
fi

bash /Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/fetch_recent_feeds.sh "${FETCH_ARGS[@]}"
```

说明：
- 统一使用 `fetch_recent_feeds.sh`，不要在会话里临时手写 `while read` 抓取循环
- 这个脚本会用独立文件描述符读取 `feeds.md`，避免循环体里的命令意外影响后续 feed 读取，解决"只抓到第一个 feed"的问题
- `CUTOFF_EPOCH` 由脚本内部计算，无需在外层重复维护

默认输出目录：
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/raw.json`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity.json`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity-structured.json`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity-structured-geo.json`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity-summary.png`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity-structured.md`
- `{EXEC_DIR}/activity-push/{yyyyMMdd}/activity-push.txt`

注意：
- 不要再用 `jq fromdateiso8601` 解析带时区偏移的时间；它对 `+08:00` 这类格式并不可靠。
- 当前推荐做法是让 `jq` 只负责拆出文章，再由 bash 的 `date` 解析时间。
- 如果某个 feed 的 `updated` 仍然无法被 `date` 解析，保留已抓取结果并在回复中明确说明该 feed 的时间格式不兼容当前 bash 过滤逻辑。
- 如果没有任何文章，也要生成 `raw.json`，内容必须是 `[]`。
- 如果公开 feed 不需要鉴权，应允许在未设置 `MP_API_KEY` 的情况下继续执行。
- 如果接口返回 401 / 403，再明确提示用户补充 `MP_API_KEY`。

### 3. 由模型判断哪些文章真的是活动，并生成 `activity.json`

这里不要做关键字筛选。你要直接阅读 `raw.json` 里的文章内容，按语义判断。

判定为"活动"的标准是：
- 文章的主要目的，是邀请用户在某个时间段参与一个具体安排，而不是单纯传递资讯
- 文中存在明确或隐含的参与动作，例如报名、预约、到场、线上进入、提交申请、加入议程
- 文章围绕一次具体事件展开，通常能对应到时间、地点、参与方式、人数、议程、对象或组织方中的若干项
- 活动主题必须明确，用户能清楚知道这是围绕什么主题、什么内容展开的活动
- 即便没有写出"活动"二字，只要本质上是在组织一次可参与的时间性事件，也算活动

不要判定为"活动"的内容：
- 活动复盘、会后总结、现场回顾
- 行业资讯、观点评论、融资新闻、产品公告
- 招聘、招生、课程长期售卖页，除非它明确对应一个具体场次或时间段
- 纯资料下载、白皮书发布、功能上线通知
- 主题模糊、内容空泛、看不出核心议题或实际安排的活动通知
- 招聘会、宣讲招聘、岗位双选会、人才招募会
- 有奖征集、征文征集、作品征集、评选征集、抽奖征集等拉新型活动

边界情况按下面处理：
- "征集 / 招募 / 训练营 / 路演 / Demo Day / Webinar / 闭门会"：如果用户需要在某个时间窗口内参与，通常算活动
- "长期社群招募 / 常年报名"：如果没有明确场次或时间边界，通常不算活动
- "直播预告"：如果有具体播出时间和参与入口，算活动
- 但如果活动主题本身不明确，或本质是招聘 / 有奖征集，即使存在时间窗口，也不要算活动

生成 `activity.json` 时：
- 文件内容必须是 `raw.json` 子集组成的 JSON 数组
- 保留原文章对象，不要先结构化
- 只保留你确信属于活动的文章
- 无活动时写入 `[]`

`activity.json` 推荐保持这种形式：

```json
[
  {
    "mpId": "gh_xxx",
    "mpName": "某公众号",
    "sourceTitle": "活动原文标题",
    "sourceUrl": "https://example.com/post/1",
    "sourceUpdated": "2026-03-11T10:00:00+08:00",
    "summary": "原文摘要",
    "content": "原文正文或正文摘要"
  }
]
```

如果 `raw.json` 中原始文章对象字段更多：
- 可以原样保留
- 但不要在 `activity.json` 中发明新的结构化字段
- `activity.json` 的角色只是"被判定为活动的原文集合"

复核时优先保证这些字段：

```json
{
  "activityName": "活动名称",
  "activityType": "活动类型",
  "activityAddress": "活动地址",
  "activityStartTime": "活动开始时间",
  "activityEndTime": "活动结束时间",
  "activityLimitNum": "活动限制人数",
  "activityDescription": "活动说明",
  "activityImages": ["活动图片1", "活动图片2"]
}
```

### 4. 提取结构化活动信息并生成 `activity-structured.json`

这一步仍由模型阅读 `activity.json` 后完成，不要用关键字脚本推断。

要求：
- 按文章语义提取活动名称、类型、地址、开始时间、结束时间、限制人数、说明、图片
- 字段缺失时使用空字符串 `""`，图片缺失时使用空数组 `[]`
- 如果同一活动重复出现在多篇文章中，按"同一事件实体"去重，而不是只看标题是否完全一致
- 去重时综合活动名称、时间、地点、组织方、议程内容判断
- 如果活动主题不明确，或属于招聘会 / 有奖征集这类明确排除项，不要进入 `activity-structured.json`
- 每条活动都要做内部价值评分，并按评分结果排序
- `activity-structured.json` 必须按活动价值从高到低输出，价值最高的活动排在最前面
- 输出必须是 JSON 数组

为保证汇总图里一定能生成二维码，每条活动都必须保留这些来源字段：
- `sourceUrl`
- `sourceTitle`
- `sourceMpId`
- `sourceMpName`

`activity-structured.json` 必须尽量贴近下面的结构：

```json
[
  {
    "activityName": "活动名称",
    "activityType": "活动类型",
    "activityAddress": "活动地址",
    "activityStartTime": "2026-03-12 14:00",
    "activityEndTime": "2026-03-12 17:00",
    "activityLimitNum": "50",
    "activityDescription": "活动说明",
    "activityImages": [
      "https://example.com/image-1.jpg"
    ],
    "sourceUrl": "https://example.com/post/1",
    "sourceTitle": "活动原文标题",
    "sourceMpId": "gh_xxx",
    "sourceMpName": "某公众号"
  }
]
```

字段约束：
- `activityName`：必须是用户能直接识别的活动名，不要只写"报名通知"
- `activityType`：例如讲座、分享会、工作坊、训练营、路演、直播、闭门会
- `activityAddress`：线下写详细地点，线上写"线上"或具体参与方式
- `activityStartTime` / `activityEndTime`：尽量统一成 `YYYY-MM-DD HH:mm`
- `activityLimitNum`：仅保留数字；未知时写空字符串
- `activityDescription`：1 到 3 句，不要整段照抄原文
- `activityImages`：必须是数组
- `sourceUrl`：必须保留原文链接，供汇总图把二维码直接渲染进图片；缺失时不允许静默省略二维码

活动价值评分时优先考虑：
- 对目标用户是否有直接价值，是否值得立即行动
- 主办方、嘉宾、合作方是否可靠，资源是否稀缺
- 时间、地点、报名方式、门槛、截止时间是否明确
- 活动是否具体可执行，而不是泛泛宣传
- 是否有明确名额、报名窗口或时效性

评分字段只用于内部排序，不要默认写入最终面向用户的 `activity-structured.json`、Markdown、图片或推送文本。

排序规则：
- 先按内部评分降序排列
- 若分数相同，优先开始时间更近且信息更完整的活动
- 若仍然相同，优先主办方更可靠、参与门槛更清晰的活动

落盘时优先保证 JSON 合法。推荐用下面方式写入：

```bash
printf '%s\n' "${STRUCTURED_JSON}" | jq '.' > "${OUT_DIR}/activity-structured.json"
```

### 4.5 使用高德地理编码补全坐标和静态地图 URL，并生成 `activity-structured-geo.json`

如果某条活动存在 `activityAddress`，应继续补全坐标。

执行入口：

```bash
python3 /Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/amap_geocode_wgs84.py \
  --input "${OUT_DIR}/activity-structured.json" \
  --output "${OUT_DIR}/activity-structured-geo.json" \
  --amap-key "${AMAP_WEB_SERVICE_KEY}"
```

本地 fixture 验证可用：

```bash
python3 /Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/amap_geocode_wgs84.py \
  --input "${OUT_DIR}/activity-structured.json" \
  --output "${OUT_DIR}/activity-structured-geo.json" \
  --fixture-file /Users/yujian/Code/py/aj-skills/skills/activity-push/tests/fixtures/amap-geocode/responses.json
```

补全规则：
- 若 `activityAddress` 为空，坐标字段和静态图 URL 置空，`activityGeoStatus` / `activityStaticMapStatus` 设为 `skipped`
- 若地址过于模糊、没有精确到可落图的地点，直接跳过地理编码，`activityGeoStatus` / `activityStaticMapStatus` 设为 `skipped_vague`
- 若高德未命中地址，坐标字段和静态图 URL 置空，`activityGeoStatus` / `activityStaticMapStatus` 设为 `not_found`
- 若命中地址，保留高德返回坐标为 GCJ-02，并额外补出 WGS84
- 若提供了 `AMAP_WEB_SERVICE_KEY`，同时拼出不带 marker 的高德静态地图 URL，供最终 Markdown 直接引用

这里的"模糊地址"包括但不限于：
- 只有"线上""腾讯会议""直播间"这类非线下地点
- 只有"报名后通知""另行通知""详见海报"这类未给出实体位置的描述
- 只有城区、附近、周边等大范围位置，没有具体门牌、楼宇或明确 POI

推荐追加这些字段：
- `activityLongitudeGCJ02`
- `activityLatitudeGCJ02`
- `activityLongitudeWGS84`
- `activityLatitudeWGS84`
- `activityGeoProvider`
- `activityGeoStatus`
- `activityStaticMapUrl`
- `activityStaticMapStatus`

坐标系说明：
- 高德地理编码结果按高德坐标处理
- 根据高德坐标系说明，这里把返回的 `location` 视为 GCJ-02
- 若用户需要 WGS84，则由本地转换公式补出
- 更详细说明见 [`amap-geocode-wgs84.md`](/Users/yujian/Code/py/aj-skills/skills/activity-push/references/amap-geocode-wgs84.md)

### 5. 使用 Python CLI + PIL 基于 `activity-structured-geo.json` 渲染汇总图片

在推送前，先把结构化活动信息渲染为一张图片，便于人工审阅、归档或后续接入图片消息链路。

执行入口：

```bash
python3 /Users/yujian/Code/py/aj-skills/skills/activity-push/scripts/render_activity_image.py \
  --input "${OUT_DIR}/activity-structured-geo.json" \
  --output "${OUT_DIR}/activity-summary.png" \
  --title "活动情报速递" \
  --subtitle "$(date +%F)"
```

要求：
- 输入优先使用 `activity-structured-geo.json`
- 输出固定为单张 PNG
- 图片中只渲染实际存在的数据字段；缺失字段直接省略，不要写"未说明""待补充"等占位词
- 只有在活动具备有效经纬度时才显示地图预览；没有经纬度时不要渲染地图占位块
- 若存在 `activityStaticMapUrl` 且有有效经纬度，可把静态地图贴进图片；地图图面不要再额外叠加 marker、十字线或高亮点
- 只要图片里渲染了活动卡片，就必须在每个活动卡片内生成原文链接二维码；二维码不能作为可选项被省略
- 若某条活动缺少 `sourceUrl`，应视为数据不完整并直接报错，而不是继续产出一个没有二维码的活动图片
- 二维码区域不要使用红色强调条，也不要写"链接已转为二维码"这类无效说明
- 无活动时也要生成空结果图片，便于归档

推荐输出：
- `{EXEC_DIR}/{yyyyMMdd}/activity-summary.png`

### 5.5 生成审阅用 Markdown 和 API 推送用纯文本

优先使用 `activity-structured-geo.json` 作为输入；若未执行坐标补全，再回退到 `activity-structured.json`。

将结构化结果保存为：
- `{EXEC_DIR}/{yyyyMMdd}/activity-structured.md`
- `{EXEC_DIR}/{yyyyMMdd}/activity-push.txt`

`activity-structured.md` 要求：
- 标题简洁，适合群消息
- 每个活动单独一节
- 活动顺序必须与 `activity-structured.json` 保持一致，按价值从高到低展示
- 优先展示：活动名称、时间、地点、人数、活动说明
- 缺失字段直接省略，不要输出"待补充""未说明"
- 若存在 `activityStaticMapUrl`，直接展示静态地图图片或图片链接
- 不要在最终 Markdown 里展示经纬度字段
- 若内容过长，先在文件中拆成多个二级标题段，便于人工审阅
- 无活动时明确写"最近 24 小时未发现新的活动文章"

`activity-structured.md` 推荐使用这个模板：

```markdown
# 活动情报速递（YYYY-MM-DD）

> 最近 24 小时筛选出的活动信息如下。

## 1. 活动名称
- 类型：活动类型
- 时间：2026-03-12 14:00 - 2026-03-12 17:00
- 地点：活动地址
- 地图：![活动地点静态图](https://restapi.amap.com/v3/staticmap?location=121.436525,31.194729&zoom=15&size=750*300&scale=2&key=YOUR_AMAP_WEB_SERVICE_KEY)
- 人数：50
- 说明：活动说明
- 来源：某公众号 / https://example.com/post/1

## 2. 活动名称
- 类型：活动类型
- 地点：线上
- 说明：活动说明
- 来源：某公众号 / https://example.com/post/2
```

无活动时固定写成：

```markdown
# 活动情报速递（YYYY-MM-DD）

最近 24 小时未发现新的活动文章。
```

推荐用下面方式落盘：

```bash
cat > "${OUT_DIR}/activity-structured.md" <<'EOF'
${ACTIVITY_STRUCTURED_MARKDOWN}
EOF
```

`activity-push.txt` 是用于 webhook 推送的文本内容，要求：
- 纯文本，不使用 Markdown 语法
- 适当压缩长度，避免过长导致成员端不愿发送
- 活动顺序必须与 `activity-structured.json` 保持一致，按价值从高到低排列
- 第一屏优先给出最值得推送的 1 到 3 个活动
- 缺失字段直接省略，不要输出"待补充""未说明"
- 每条活动建议控制在 2 到 5 行
- **无活动时不生成此文件或内容为空，不推送消息到群**

推荐模板：

```text
活动情报速递（YYYY-MM-DD）

1. 活动名称
类型：活动类型
时间：2026-03-12 14:00 - 2026-03-12 17:00
地点：活动地址
说明：活动说明
链接：https://example.com/post/1

2. 活动名称
类型：活动类型
地点：线上
说明：活动说明
链接：https://example.com/post/2
```

推荐用下面方式落盘：

```bash
cat > "${OUT_DIR}/activity-push.txt" <<'EOF'
${ACTIVITY_PUSH_TEXT}
EOF
```

### 6. 使用 Webhook 推送到内部群

这一步是可选步骤，用于将活动信息推送到企业微信内部群。

**特点**：
- ✅ 无需 access_token，只需 webhook key
- ✅ 即时发送，无需成员确认
- ❌ 仅支持内部群，外部群不支持

**添加群机器人**：
1. 企业微信客户端 → 进入内部群 → 群设置
2. 群机器人 → 添加机器人
3. 复制 Webhook 地址中的 key 部分：`xxxxxx`

**环境变量配置**（`~/.aj-skills/.env`）：
```bash
# 单群
WE_COM_WEBHOOK_KEYS=2449ebfdd2b2a1f20d88f797e3627d8fc6
# 多群（逗号分隔）
WE_COM_WEBHOOK_KEYS=key1,key2,key3
```

**推送命令**：
```bash
# 检查是否有活动（activity.json 不为空数组）
ACTIVITY_COUNT=$(jq 'length' "${OUT_DIR}/activity.json")

if [ "$ACTIVITY_COUNT" -eq 0 ]; then
  echo "No activities found, skipping push"
elif [ -n "${WE_COM_WEBHOOK_KEYS:-}" ]; then
  # 读取消息内容并转义为 JSON 字符串
  MESSAGE=$(cat "${OUT_DIR}/activity-push.txt" | jq -Rs '.')

  # 遍历所有 key 进行推送（兼容 bash/zsh）
  echo "$WE_COM_WEBHOOK_KEYS" | tr ',' '\n' | while IFS= read -r key; do
    key=$(echo "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')  # 去除空格
    [ -z "$key" ] && continue
    echo "Pushing to webhook: ${key:0:8}..."
    curl -s "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=$key" \
      -H 'Content-Type: application/json' \
      -d "{\"msgtype\":\"text\",\"text\":{\"content\":$MESSAGE}}" | jq .
  done
else
  echo "skip push: WE_COM_WEBHOOK_KEYS not configured"
fi
```

**限制说明**：
- 仅内部群支持 webhook，外部群不支持
- 详见 [`wecom-group-types-guide.md`](/Users/yujian/Code/py/aj-skills/skills/activity-push/references/wecom-group-types-guide.md)

### 6.1 推送图片

Webhook 也支持推送图片，但**需要先上传图片获取 media_id**。

**上传图片获取 media_id**：
```bash
# 上传图片（key 是机器人的 webhook key）
curl -F "key=YOUR_KEY" \
     -F "media=@activity-summary.png" \
     "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?type=image" | jq -r '.media_id'
```

**推送图片消息**：
```bash
# 使用获取到的 media_id 推送图片
curl -s "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "msgtype": "image",
    "image": {
      "media_id": "MEDIA_ID_FROM_UPLOAD"
    }
  }' | jq .
```

**同时推送文字+图片**：
```bash
# 先推送文字
MESSAGE=$(cat "${OUT_DIR}/activity-push.txt" | jq -Rs '.')
curl -s "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
  -H 'Content-Type: application/json' \
  -d "{\"msgtype\":\"text\",\"text\":{\"content\":$MESSAGE}}"

# 再推送图片
MEDIA_ID=$(curl -s -F "key=YOUR_KEY" -F "media=@${OUT_DIR}/activity-summary.png" \
  "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?type=image" | jq -r '.media_id')

curl -s "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=YOUR_KEY" \
  -H 'Content-Type: application/json' \
  -d "{\"msgtype\":\"image\",\"image\":{\"media_id\":\"$MEDIA_ID\"}}" | jq .
```

**注意**：
- 图片大小不能超过 2MB
- media_id 3 天内有效
- 支持的格式：png, jpg, jpeg, gif, bmp, webp

## Output Rules

- `raw.json` 必须是最近 24 小时文章组成的 JSON 数组
- `activity.json` 必须是活动候选文章组成的 JSON 数组
- `activity-structured.json` 必须是去重后的活动对象数组
- `activity-structured.json` 必须按内部评分结果降序排列
- `activity-structured-geo.json` 必须在有地址时尽量补全 GCJ-02、WGS84 和静态地图 URL
- `activity-summary.png` 必须由 `activity-structured-geo.json` 渲染生成；空结果也要产出
- `activity-summary.png` 在存在活动时，每个活动卡片都必须包含二维码
- `activity-structured.md` 必须用于人工审阅，默认中文
- `activity-structured.md` 不展示坐标字段，优先展示静态地图
- `activity-push.txt` 必须用于 webhook 推送的文本内容

如果没有活动：
- 仍然生成所有目标文件
- `activity.json` 与 `activity-structured.json` 为空数组 `[]`
- `activity-structured-geo.json` 也应为空数组 `[]`
- `activity-summary.png` 仍应生成空结果图片
- `activity-structured.md` 写明"最近 24 小时未发现新的活动文章"
- **`activity-push.txt` 为空文件或不生成，不推送"无活动"消息到群**

## Semantic Judgment Rules

判断"是否是活动"时，始终用下面的思路，而不是查词：

1. 先看文章的核心意图
如果文章的中心是在组织一次参与行为，它更可能是活动；如果中心只是表达观点、传递新闻或做总结，就不是活动。

2. 再看是否存在"参与闭环"
活动通常会形成一个闭环：谁可以参加、何时参加、在哪里参加、怎样参加、参加后发生什么。即使其中某些字段缺失，只要闭环大体成立，就可判为活动。

3. 再看时间性和事件性
活动是一个具体事件，通常有场次、时间窗口或明确排期。长期存在、没有明确场次的介绍页，通常不应视为活动。

4. 最后看文章是否要求读者采取行动
如果读者被要求报名、预约、进群、到场、观看直播、提交资料、参与议程，这通常说明它是活动。

## WeCom Push Rules

- 使用群机器人 webhook 推送到内部群
- 消息正文使用纯文本，不要把 Markdown 原样发送
- 支持多群同时推送（逗号分隔多个 key）
- 只有在 `WE_COM_WEBHOOK_KEYS` 配置存在时才执行第 6 步

## Quality Checklist

- 已完成环境预检
- 已用 bash + `curl` + `jq` 完成抓取
- 已按 `updated` 过滤最近 24 小时文章
- 已产出 `raw.json`
- 已由模型按语义判断活动候选并产出 `activity.json`
- 已提取结构化字段并去重
- 已产出 `activity-structured.json`
- 已完成活动价值评分并按高到低排序
- 如地址存在，已产出 `activity-structured-geo.json`
- 已产出 `activity-summary.png`
- 已确认所有活动卡片都带有二维码
- 已产出审阅用 `activity-structured.md`
- 已产出推送用 `activity-push.txt`
- 若推送配置完整，已通过 webhook 完成推送
- 回复中明确给出所有输出文件路径
- 如处于开发或调试阶段，已至少运行一次 CLI dry-run 或本地测试

## Failure Handling

如果发生错误，按下面顺序处理：

1. 先定位是输入缺失、网络失败、字段不兼容，还是 webhook 调用失败
2. 能继续的步骤继续执行，不要因为单个公众号失败就中止全部流程
3. 在终端输出中保留失败原因摘要
4. 如果 feed JSON 结构不兼容，先保存原始结果，再说明使用了什么字段假设
5. 如果 webhook 返回错误，检查 key 是否有效、群是否还存在
6. 如果企业微信推送配置缺失，直接跳过第 6 步，不要把整个 skill 判定为失败

## Optimization Notes

相对你原始草案，这里做了这些优化：
- 不再把"是不是活动"交给关键字规则，而是交给模型做语义判断
- 全流程回到 bash + `curl` + `jq`，更贴近你要求的执行方式
- `feeds.md` 支持空行和注释
- 活动去重改为事件实体判断，而不是字符串硬匹配
- 推送链路使用 webhook 机器人，简单直接
- 审阅内容与发送内容分离，降低 API 消息体格式不兼容风险
- 活动地址支持补全高德坐标、WGS84 坐标和静态地图 URL，便于 Markdown 展示或下游系统使用
- 推送前增加 PIL 汇总图，方便人工快速过目，也为后续图片消息链路留出稳定产物
- 所有步骤都落盘，便于二次检查和重跑

## Test Prompts

可用这些提示词测试 skill 是否会正确触发：

1. "根据当前目录的 feeds.md，把最近 24 小时公众号文章里的活动提取出来，并通过 webhook 推送到企业微信群。"
2. "读取 ~/.aj-skills/.env 和 feeds.md，输出 raw.json、activity.json、activity-structured.json、activity-structured-geo.json、activity-summary.png、activity-structured.md、activity-push.txt，再通过 webhook 推送。"
3. "帮我做一个活动推送流水线：从公众号 feed 抓文章，筛活动，结构化提取，补全高德地址坐标并转成 WGS84，顺手生成静态地图 URL，再用 PIL 渲染一张活动汇总图，生成审阅 Markdown 和群发送文本，并通过 webhook 推送到企业微信群。"
