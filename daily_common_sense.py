import requests
import os
import subprocess
from datetime import datetime
from memory_utils import load_memory, add_topic

# ================= 配置 =================
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
SERVER_CHAN_KEY = os.getenv("SERVER_CHAN_KEY")
TOPIC_TYPE = "sense"  # 唯一标识，与 memory_sense.json 对应

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
            {"role": "user", "content": f"今天是{datetime.now().strftime('%Y-%m-%d')}。{ban_text} 请推送今日常识。"}
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

# ================= Git 提交记忆文件 =================
def push_memory_to_repo():
    try:
        subprocess.run(['git', 'config', 'user.name', 'github-actions'], check=False)
        subprocess.run(['git', 'config', 'user.email', 'github-actions@github.com'], check=False)
        subprocess.run(['git', 'pull', '--rebase'], check=False)
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
