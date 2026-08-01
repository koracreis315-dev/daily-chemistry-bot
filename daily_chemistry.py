import requests
import json
from datetime import datetime

# ================= 配置区（密钥从环境变量读取）=================
import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")

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

# ================= 调用 DeepSeek API（带详细错误输出）=================
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

    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"HTTP状态码: {response.status_code}")  # 关键：打印状态码
        print(f"API原始响应: {response.text}")       # 关键：打印原始内容

        if response.status_code != 200:
            print("API请求失败，请检查上述响应中的错误信息。")
            return None

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except Exception as e:
        print(f"请求或解析过程中发生异常: {e}")
        return None

# ================= 推送到微信 =================
def send_to_wechat(content):
    if content is None:
        print("内容为空，不推送。")
        return False

    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {
        "title": f"【每日化学】{datetime.now().strftime('%Y-%m-%d')}",
        "desp": content
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        print(f"Server酱响应: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"推送异常: {e}")
        return False

# ================= 主程序 =================
if __name__ == "__main__":
    print("开始生成今日化学推理...")
    text = get_daily_chemistry()
    if text:
        print("内容生成成功，正在推送...")
        if send_to_wechat(text):
            print("推送成功！")
        else:
            print("推送失败，请检查 Server酱 配置。")
    else:
        print("内容生成失败，请检查上方API输出。")
