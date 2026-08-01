import requests
import json
from datetime import datetime

# ================= 配置区 =================
# 请替换成你自己的密钥（后续会放在GitHub Secrets里，此处留空）
DEEPSEEK_API_KEY = "YOUR_DEEPSEEK_API_KEY"
SERVER_CHAN_KEY = "YOUR_SERVER_CHAN_KEY"

# ================= 智能体核心 Prompt =================
SYSTEM_PROMPT = """
你是一位严谨的化学推理官。请严格遵守以下四步结构推送今天的化学知识：
1. 现象引入（日常生活）
2. 核心原理（微观电子/分子层面，必要时提及量子跃迁）
3. 论证实验（具体操作与预期现象）
4. 对比实验（**必须用表格**对比实验组与对照组，控制单一变量）
5. 结论（总结充要条件）
要求：语言生动，逻辑严密，今天的内容请围绕“厨房中的化学”展开。
"""

# ================= 调用 DeepSeek API =================
def get_daily_chemistry():
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"今天是{datetime.now().strftime('%Y-%m-%d')}，请推送今日化学知识。"}
        ],
        "temperature": 0.7,
        "max_tokens": 2000
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"]

# ================= 通过 Server酱 推送到微信 =================
def send_to_wechat(content):
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {
        "title": f"【每日化学】{datetime.now().strftime('%Y-%m-%d')}",
        "desp": content
    }
    response = requests.post(url, data=data)
    return response.status_code == 200

# ================= 主程序 =================
if __name__ == "__main__":
    print("开始生成今日化学推理...")
    try:
        text = get_daily_chemistry()
        print("内容生成成功，正在推送...")
        if send_to_wechat(text):
            print("推送成功！")
        else:
            print("推送失败，请检查 Server酱 配置。")
    except Exception as e:
        print(f"任务执行出错: {e}")