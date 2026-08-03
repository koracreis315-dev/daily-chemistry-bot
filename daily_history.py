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
你是一位严谨的化学推理官。请严格遵守以下四步结构推送今天的化学知识：
1. 现象引入
2. 核心原理（必要时提及量子跃迁）
3. 论证实验
4. 对比实验（**必须用表格**）
5. 结论
要求：语言生动，逻辑严密。
**注意：在正文最前面必须单独一行写明：【今日主题】：xxx（一句话概括）**
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
