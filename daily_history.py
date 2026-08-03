import requests
import os
from datetime import datetime

# ================= 从环境变量读取密钥 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")
TOPIC_TYPE = "history"

# ================= 历史人物专属提示词 =================
SYSTEM_PROMPT = """
你是一位博学的历史档案员，擅长从浩瀚史海中打捞有趣的人物。你的使命是每天为用户推荐一位历史人物，让用户感受历史的温度与深度。

选人范围：不限于帝王将相，可以包含科学家、工匠、诗人、医生、探险家、商人、刺客、隐士，甚至是史书角落里的“小人物”。只要在正史、野史或可靠考古发现中有记载即可。每天尽量切换不同时代、不同地域、不同职业。

请严格遵守以下结构输出（必须使用 Markdown 格式）：

**【人物档案】**
- **姓名**：全名及常见称号
- **时代与身份**：生活年代、国籍/朝代、主要身份标签（例如：北宋天文学家、维京探险家）

**【生平经历】**
概述其一生关键节点（出身、重要转折、结局）。

**【核心事件】**
提取其人生中最具代表性的一件事或一项成就，详细展开。

**【对历史的影响】**
该人物的存在对当时或后世产生了什么影响？（思想、技术、制度、文化等）

**【对重大事件的影响】**
如果该人物间接影响了某个重大历史事件（如战争、变法、地理大发现），请具体指出；如果无关或无直接影响，请直接写 **“无”**。

**【冷知识/趣味标签】**
用一句话说出他/她身上最反直觉或最有趣的一个小细节。

输出要求：
- 语言简洁有力，避免过度抒情。
- 如果涉及争议人物，客观陈述史实，不站队。
"""

# ================= 调用 DeepSeek API =================
def get_daily_history():
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"今天是{datetime.now().strftime('%Y-%m-%d')}，请推荐今日历史人物。"}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"HTTP状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"API错误响应: {response.text}")
            return None
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"请求异常: {e}")
        return None

# ================= 推送微信 =================
def send_to_wechat(content):
    if content is None:
        print("内容为空，不推送。")
        return False
    
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {
        "title": f"【每日历史人物】{datetime.now().strftime('%Y-%m-%d')}",
        "desp": content
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        print(f"推送响应: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"推送异常: {e}")
        return False

# ================= 主程序 =================
if __name__ == "__main__":
    print("开始生成今日历史人物...")
    text = get_daily_history()
    if text:
        if send_to_wechat(text):
            print("历史人物推送成功！")
        else:
            print("历史人物推送失败。")
    else:
        print("历史人物生成失败。")
