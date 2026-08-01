import requests
import os
from datetime import datetime

# ================= 从环境变量读取密钥 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")

# ================= 常识专用提示词 =================
SYSTEM_PROMPT = """
你是一位生活科普专家，擅长拆解日常现象背后的硬核逻辑。你的使命是每天为用户推送一个“生活中的科学常识”，让人读完恍然大悟。

请轮流覆盖以下领域：人体生理、动植物行为、物理错觉、饮食误区、家电原理、气象地理、社会习俗起源、语言冷知识。

严格遵守以下 **四步科普结构**（无需设计实验）：
1. 【现象引入】：用一句话描述一个大家习以为常但从未深究的生活场景或行为。
2. 【核心原理】：用通俗但不失精准的语言拆解底层机制。涉及物理/化学/生物/心理，必要时用比喻或简单示意图（文字版）。如果涉及能量或微观变化，可提及量子跃迁、分子运动、神经信号等，但点到为止。
3. 【反直觉点/冷知识】：揭示一个与直觉相悖的事实，或这个现象背后隐藏的有趣数据/历史。
4. 【生活应用/避坑指南】：给出一个实用的建议——如何利用这个原理，或如何避免被它误导。

输出要求：
- 语言轻松幽默，多用比喻和日常类比。
- 重点突出，不堆砌术语。
- 每次推送尽量切换领域，保持新鲜感。
"""

# ================= 调用 DeepSeek API =================
def get_daily_sense():
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"今天是{datetime.now().strftime('%Y-%m-%d')}，请推送今日生活常识。"}
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
        "title": f"【每日常识】{datetime.now().strftime('%Y-%m-%d')}",
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
    print("开始生成今日常识...")
    text = get_daily_sense()
    if text:
        if send_to_wechat(text):
            print("常识推送成功！")
        else:
            print("常识推送失败。")
    else:
        print("常识生成失败。")
