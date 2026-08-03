import requests
import os
import subprocess
from datetime import datetime
from memory_utils import load_memory, add_topic  # 导入新工具

# ================= 配置 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")
TOPIC_TYPE = "chemistry"  # ！！！常识改成 "sense"，历史改成 "history" ！！！

# ================= 系统提示词（不变）=================
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

# ================= 调用 API（带记忆禁令）=================
def get_daily_content():
    # 1. 加载该类型的已有主题列表
    history_list = load_memory(TOPIC_TYPE)
    
    # 2. 构建禁令（只拿最近50条塞给AI，既省Token又能有效避雷）
    ban_text = ""
    if history_list:
        recent = history_list[-50:]
        ban_text = f"**严格禁止重复以下已经讲过的主题**：{', '.join(recent)}。请务必选择一个全新的、未提及的主题。"
    
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"今天是{datetime.now().strftime('%Y-%m-%d')}。{ban_text} 请推送今日内容。"}
        ],
        "temperature": 0.8,
        "max_tokens": 2000
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"HTTP状态码: {response.status_code}")
        if response.status_code != 200:
            print(f"API错误: {response.text}")
            return None
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        
        # 3. 提取主题并存入对应的独立文件
        topic = "未知主题"
        for line in content.split('\n'):
            if line.strip().startswith('【今日主题】'):
                topic = line.strip().replace('【今日主题】', '').strip()
                break
        if topic == "未知主题":
            topic = content[:15].replace('\n', '') + "..."
        
        # 自动追加并自动裁切（超过100条会删最旧的）
        add_topic(TOPIC_TYPE, topic)
        print(f"已记录主题: {topic} (当前该类型共 {len(load_memory(TOPIC_TYPE))} 条)")
        
        return content
    except Exception as e:
        print(f"请求异常: {e}")
        return None

# ================= 推送微信 =================
def send_to_wechat(content):
    if content is None:
        return False
    url = f"https://sctapi.ftqq.com/{SERVER_CHAN_KEY}.send"
    data = {
        "title": f"【每日{ '化学' if TOPIC_TYPE=='chemistry' else '常识' if TOPIC_TYPE=='sense' else '历史人物' }】{datetime.now().strftime('%Y-%m-%d')}",
        "desp": content
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        print(f"推送响应: {resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"推送异常: {e}")
        return False

# ================= Git 提交（改成分文件提交）=================
def push_memory_to_repo():
    try:
        subprocess.run(['git', 'config', 'user.name', 'github-actions'], check=False)
        subprocess.run(['git', 'config', 'user.email', 'github-actions@github.com'], check=False)
        subprocess.run(['git', 'pull', '--rebase'], check=False)
        # 关键改动：用 git add . 把所有 memory_*.json 都提交，或者精准提交当前类型的文件
        subprocess.run(['git', 'add', f'memory_{TOPIC_TYPE}.json'], check=False)
        subprocess.run(['git', 'commit', '-m', f'更新{TOPIC_TYPE}记忆 - {datetime.now().strftime("%Y-%m-%d")}'], check=False)
        subprocess.run(['git', 'push'], check=False)
        print(f"记忆文件 memory_{TOPIC_TYPE}.json 已提交到仓库。")
    except Exception as e:
        print(f"Git提交失败（不影响推送）: {e}")

# ================= 主程序 =================
if __name__ == "__main__":
    print(f"开始生成今日 {TOPIC_TYPE} 内容...")
    text = get_daily_content()
    if text:
        if send_to_wechat(text):
            print("推送成功！正在保存记忆...")
            push_memory_to_repo()
        else:
            print("推送失败。")
    else:
        print("生成失败。")
