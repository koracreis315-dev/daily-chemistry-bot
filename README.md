⚙️ 第一步：准备工作
注册账号：准备一个 GitHub 账号、DeepSeek 账号（用于获取API Key）以及 Server酱 账号（用于微信推送）。

获取密钥：在DeepSeek平台创建 API Key；在Server酱官网完成微信绑定后获取 SCKEY。

📝 第二步：准备脚本
 daily_chemistry.py

🚀 第三步：部署到 GitHub Actions
创建仓库并上传文件：在GitHub新建一个仓库（如 daily-chemistry-bot），将 daily_chemistry.py 和 requirements.txt（内容为requests）上传。

配置密钥 (Secrets)：进入仓库 Settings -> Secrets and variables -> Actions，点击 New repository secret 添加两个密钥：

DEEPSEEK_API_KEY：你的DeepSeek API Key。

SERVER_CHAN_KEY：你的Server酱 SCKEY。

创建工作流文件：在仓库中创建 .github/workflows/daily.yml

🔍 第四步：验证与调试
手动触发：在GitHub仓库的 Actions 选项卡，选中 Daily Chemistry Bot，点击 Run workflow 手动运行一次。

检查日志：点击正在运行的工作流，可实时查看输出日志。如有报错，可根据日志排查。
