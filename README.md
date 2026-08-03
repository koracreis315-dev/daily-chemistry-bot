```
📚 每日知识推送机器人

基于 GitHub Actions 和 DeepSeek API 实现的自动化知识推送系统。每天定时向微信推送三份风格各异的知识简报：化学推理、生活常识、历史人物。

✨ 核心特性

- 🧪 每日化学：严谨的四步推理（现象→原理→论证实验→对比实验），培养科学思维。
- 🧠 每日常识：轻松有趣的科普短文（现象→原理→冷知识→避坑指南），专治各种“习以为常”。
- 👤 每日历史人物：打捞史海遗珠，还原人物生平、核心事件及历史影响。
- 💾 记忆机制：自动记录已推送的主题，确保每天内容不重复（每种类型独立记忆，最多保留 100 条）。

📁 项目文件结构
.
├── .github/
│   └── workflows/
│       ├── daily.yml                 # 化学推送工作流
│       ├── daily_sense.yml           # 常识推送工作流
│       └── daily_history.yml         # 历史推送工作流
│
├── daily_chemistry.py                # 化学推送核心脚本
├── daily_sense.py                    # 常识推送核心脚本
├── daily_history.py                  # 历史推送核心脚本
├── memory_utils.py                   # 记忆管理工具箱
│
├── memory_chemistry.json             # 自动生成：化学已推主题
├── memory_sense.json                 # 自动生成：常识已推主题
├── memory_history.json               # 自动生成：历史已推主题
│
└── README.md                         # 项目说明文档


🚀 快速部署与配置

1. 准备密钥

| 密钥名称 | 获取方式 | 用途 |
| :--- | :--- | :--- |
| `DEEPSEEK_API_KEY` | 登录 [DeepSeek 开放平台](https://platform.deepseek.com/) 创建 API Key | 调用 DeepSeek 大模型生成内容 |
| `SERVER_CHAN_KEY` | 访问 [Server酱](https://sct.ftqq.com/) 扫码绑定微信后获取 | 推送消息到微信 |

2. 在 GitHub 仓库配置 Secrets

进入你的仓库页面 → `Settings` → `Secrets and variables` → `Actions`，点击 `New repository secret`，依次添加：

- `DEEPSEEK_API_KEY`：填入你的 DeepSeek API Key
- `SERVER_CHAN_KEY`：填入你的 Server酱 SCKEY

3. 授予 Git 推送权限（非常重要）

为了让脚本能自动把“记忆文件”提交回仓库，你需要在 三个 `.yml` 工作流文件 的 `jobs:` 上方加上以下配置：

```yaml
# ===== 关键：授予脚本 push 权限 =====
permissions:
  contents: write
```



如果缺少这一步，脚本在执行 `git push` 时会因权限不足（403）而报错，记忆功能将无法生效。

### 4. 调整推送时间（可选）

GitHub Actions 的 `cron` 使用 UTC 时间（比北京时间慢 8 小时）。
当前三个工作流的默认触发时间如下：

| 推送内容 | Cron 表达式 (UTC) | 对应北京时间 |
| :------- | :---------------- | :----------- |
| 每日化学 | `30 8 * * *`      | 当日 16:30   |
| 每日常识 | `0 9 * * *`       | 当日 17:00   |
| 每日历史 | `30 9 * * *`      | 当日 17:30   |

如需调整，例如改为北京时间早上 8:30，请将 `cron` 改为 `30 0 * * *`（UTC 0:30）。

## 🧪 手动触发测试

如果不想等定时任务，可以手动触发工作流：

1. 进入你的 GitHub 仓库，点击上方的 `Actions` 选项卡。
2. 在左侧边栏中选择对应的流水线（如 `Daily Chemistry Bot`）。
3. 点击右侧的 `Run workflow` → `Run workflow` 按钮。
4. 几秒后查看运行日志，确认 `已记录主题` 和 `推送成功` 字样。

## 🧠 记忆机制详解

- 分文件存储：化学、常识、历史各自拥有独立的记忆文件（`memory_*.json`），互不干扰。
- 自动去重：每次推送前，脚本会读取对应文件，把已讲主题作为“禁令”写入提示词，强制 AI 选择全新主题。
- 自动裁切：每种类型最多保留 100 条 记录（先进先出），防止文件无限膨胀，节省 Token 消耗。

## ⚠️ 注意事项

1. API 费用：调用 DeepSeek API 会产生少量费用（新用户通常有赠送额度），请留意余额。
2. 时区换算：配置 Cron 时务必注意 UTC 与本地时间的换算关系。
3. Git 冲突：由于三个脚本运行时间错开，且各自操作独立文件，几乎不会产生 Git 冲突。脚本已包含 `git pull --rebase` 逻辑，进一步降低风险。
4. 请以娱乐和学习心态看待，重要信息请交叉验证。

## 📄 开源许可

本项目仅供个人学习与娱乐使用，欢迎自由修改和分发。
