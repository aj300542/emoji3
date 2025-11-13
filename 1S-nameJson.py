import os
import json
from collections import defaultdict

# 设置目录路径和输出文件路径
SOURCE_DIR = 'json'
OUTPUT_FILE = 'emojiNames.json'

# 用于收集 emoji 映射
emoji_map = defaultdict(set)

# 遍历 json 目录及其子目录
for root, _, files in os.walk(SOURCE_DIR):
    for file in files:
        if file.endswith('.json'):
            path = os.path.join(root, file)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            icon = item.get('icon')
                            name = item.get('name')
                            if icon and name:
                                emoji_map[icon].add(name)
            except Exception as e:
                print(f"跳过文件 {path}，解析失败：{e}")

# 转换为字典并排序
emoji_dict = {k: sorted(list(v)) for k, v in sorted(emoji_map.items())}

# 写入输出文件
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(emoji_dict, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 {OUTPUT_FILE}，共收集 {len(emoji_dict)} 个 emoji 映射。")
