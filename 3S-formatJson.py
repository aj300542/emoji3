import json

# 输入输出路径
INPUT_FILE = 'emojiN2.json'       # 原始字典格式
OUTPUT_FILE = 'emojiList.json'  # 输出为数组格式，每行一个对象

# 加载原始数据
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    emoji_dict = json.load(f)

# 构造数组格式
emoji_list = []
for icon, names in emoji_dict.items():
    for name in names:
        emoji_list.append({"icon": icon, "name": name})

# 写入为格式化 JSON 数组，每个对象占一行
with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('[\n')
    for i, item in enumerate(emoji_list):
        line = json.dumps(item, ensure_ascii=False)
        if i < len(emoji_list) - 1:
            line += ','
        f.write(f'  {line}\n')
    f.write(']\n')

print(f"✅ 已生成 {OUTPUT_FILE}，每个 emoji 映射占一行，共 {len(emoji_list)} 条记录。")
