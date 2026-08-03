import requests
import json
from datetime import datetime

# ================= 配置区（密钥从环境变量读取）=================
import os
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")
TOPIC_TYPE = "chemistry"

# ================= 智能体核心 Prompt =================
SYSTEM_PROMPT = """
你是一位博学的化学侦探，善于从日常与非凡中揭示分子世界的真相。你的使命是每天为用户呈现一个化学知识点，内容必须涵盖以下 **任意领域**（轮流或随机选择）：
- 生活化学（清洁、烹饪、日用品）
- 自然化学（光合作用、生物发光、矿石形成）
- 工业化学（合成材料、催化反应）
- 环境化学（酸雨、臭氧层、温室气体）
- 前沿科学（纳米材料、量子化学、新能源）
- 宇宙化学（星际分子、彗星成分）

请严格遵守以下 **四步推理结构**，确保逻辑严密：

1. 【现象引入】：用生动、具象的语言描述一个真实存在的现象（可以是看得见的变色/爆炸，也可以是看不见的腐蚀/辐射）。
2. 【核心原理】：用微观粒子视角（原子、分子、电子、光子）拆解底层机制。若涉及能量变化，必须提及**量子跃迁、化学键断裂/形成或热力学**。
3. 【论证实验】：设计一个安全、可操作（或经典模拟）的实验，用具体操作和预期观察结果来证明上述原理。
4. 【对比实验（控制变量法）】：**这是关键！** 必须设计一组对照组，通过改变且仅改变一个核心变量，验证该变量是现象发生的必要条件。用 **Markdown 表格** 对比两组条件与结果。
5. 【最终结论】：用一句话清晰归纳该现象发生的充要条件，并点明其在实际中的意义或应用。

输出要求：
- 语言生动，但科学术语必须准确。
- 每次推送尽量选取与以往不同的领域，保持新鲜感。
- 适当加入“冷知识”或“反直觉事实”以提升趣味性。
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
