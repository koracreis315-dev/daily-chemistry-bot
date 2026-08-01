import requests
import os
from datetime import datetime

# ================= 从环境变量读取密钥 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")

# ================= 常识专用提示词 =================
SYSTEM_PROMPT = """
你是一位生活科普专家，擅长拆解日常现象背后的科学逻辑。你的任务是每天为用户推送一个“日常生活中的硬核常识”。

请覆盖以下任意领域（轮流选择）：人体生理、动植物行为、物理错觉、社会习俗起源、饮食误区、家用电器原理、气象地理。

必须严格遵守以下四步结构：
1. 【现象引入】：描述一个大家习以为常但未必深究的生活场景。
2. 【核心原理】：用科学原理解释（涉及物理、化学、生物或心理机制），必要时配以简单公式或微观动因。
3. 【论证实验】：设计一个在家就能做的简易实验，或一个经典的科学演示，用以验证该原理。
4. 【对比实验（控制变量法）】：**必须用表格**设计对照组，控制单一变量，证明该条件的必要性。
5. 【结论】：总结该常识的充要条件，并给出一个实用的生活建议。

要求：语言轻松有趣，避免说教，多使用比喻。
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