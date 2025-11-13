import json
from fontTools.ttLib import TTFont

# 路径配置
FONT_PATH = 'font/seguiemj-1.35-flat.ttf'
EXISTING_JSON = 'emojiNames.json'
OUTPUT_JSON = 'emojiN2.json'

# 加载字体
font = TTFont(FONT_PATH)

# 提取所有 Unicode 字符
unicode_chars = set()
for table in font['cmap'].tables:
    for codepoint in table.cmap.keys():
        try:
            char = chr(codepoint)
            # 过滤 emoji 范围（可根据需要扩展）
            if 0x1F000 <= codepoint <= 0x1FAFF or 0x2600 <= codepoint <= 0x26FF:
                unicode_chars.add(char)
        except:
            continue

# 加载已有 emojiNames.json
with open(EXISTING_JSON, 'r', encoding='utf-8') as f:
    existing = json.load(f)
    existing_emojis = set(existing.keys())

# 找出缺失 emoji
missing_emojis = sorted(unicode_chars - existing_emojis)

# 构造输出格式
output = {emoji: [] for emoji in missing_emojis}

# 写入结果
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✅ 已生成 {OUTPUT_JSON}，共发现 {len(output)} 个漏网 emoji。")
