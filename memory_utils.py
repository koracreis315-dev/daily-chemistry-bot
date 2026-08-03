import json
import os

MAX_ENTRIES = 100  # 每个类别最多保留100条，防止无限膨胀

def get_memory_path(topic_type):
    """根据类型返回对应的记忆文件路径"""
    return f"memory_{topic_type}.json"  # chemistry -> memory_chemistry.json

def load_memory(topic_type):
    """加载指定类型的记忆列表"""
    path = get_memory_path(topic_type)
    if not os.path.exists(path):
        return []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []

def save_memory(topic_type, data):
    """保存指定类型的记忆列表"""
    path = get_memory_path(topic_type)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def add_topic(topic_type, new_topic):
    """追加新主题，若超过100条则自动删掉最旧的"""
    data = load_memory(topic_type)
    if new_topic not in data:  # 防止意外重复
        data.append(new_topic)
        # 只保留最后 100 条
        if len(data) > MAX_ENTRIES:
            data = data[-MAX_ENTRIES:]
        save_memory(topic_type, data)
    return data
