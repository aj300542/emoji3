from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import svgwrite
import json
import os
import time

# ✅ 参数设置
FONT_PATH = r"Z:\2025\emoji135\font\seguiemj-1.35-flat.ttf"
OUTPUT_ROOT = r"Z:\2025\emoji135\emoji_export"
SIZE = 256  # SVG 尺寸

# ✅ 创建根输出目录
os.makedirs(OUTPUT_ROOT, exist_ok=True)

# ✅ 加载字体
font = TTFont(FONT_PATH)
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()

# ✅ 检查是否支持 COLR/CPAL
if "COLR" not in font or "CPAL" not in font:
    raise ValueError("该字体不支持 COLR/CPAL 彩色图层结构")

colr = font["COLR"]
cpal = font["CPAL"]
palette = cpal.palettes[0]  # 使用第一个调色板

# ✅ 收集所有可导出的 emoji
emoji_entries = []
for codepoint, glyph_name in cmap.items():
    if glyph_name in colr.ColorLayers and colr.ColorLayers[glyph_name]:
        emoji_entries.append((codepoint, glyph_name))

total = len(emoji_entries)
print(f"📦 共发现 {total} 个可导出的 emoji")

# ✅ 开始计时
start_time = time.time()

# ✅ 导出每个 emoji
for count, (codepoint, base_glyph) in enumerate(emoji_entries, start=1):
    emoji_char = chr(codepoint)
    emoji_code = f"U+{codepoint:04X}"
    emoji_dir = os.path.join(OUTPUT_ROOT, emoji_code)
    os.makedirs(emoji_dir, exist_ok=True)

    layers = colr.ColorLayers[base_glyph]
    layer_metadata = []

    emoji_start = time.time()

    for i, layer in enumerate(layers):
        glyph_name = layer.name
        color_index = layer.colorID
        bgra = palette[color_index]

        # ✅ 修正颜色顺序：BGRA → RGBA
        b, g, r = bgra[:3]
        r = r if isinstance(r, int) else 0
        g = g if isinstance(g, int) else 0
        b = b if isinstance(b, int) else 0

        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

        # ✅ 提取路径
        pen = SVGPathPen(glyph_set)
        glyph_set[glyph_name].draw(pen)
        path_data = pen.getCommands()

        # ✅ 保存 SVG 文件
        svg_filename = f"emoji_layer_{i:02d}.svg"
        svg_path = os.path.join(emoji_dir, svg_filename)
        dwg = svgwrite.Drawing(svg_path, size=(SIZE, SIZE))
        dwg.add(dwg.path(
            d=path_data,
            style=f"fill:{hex_color};stroke:none",
            transform=f"scale(1,-1) translate(0,-{SIZE})"
        ))
        dwg.save()

        layer_metadata.append({
            "layer_index": i,
            "glyph_name": glyph_name,
            "color": {"r": r, "g": g, "b": b},
            "hex": hex_color,
            "svg_file": svg_filename
        })

    # ✅ 保存 JSON 文件
    json_path = os.path.join(emoji_dir, "emoji_layers_metadata.json")
    output_data = {
        "emoji_char": emoji_char,
        "emoji_code": emoji_code,
        "layers": layer_metadata
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)

    emoji_time = time.time() - emoji_start
    percent = (count / total) * 100
    print(f"✅ {emoji_char} ({emoji_code}) → {len(layer_metadata)} 层 | {count}/{total} ({percent:.1f}%) | ⏱️ {emoji_time:.2f}s")

# ✅ 总用时
elapsed = time.time() - start_time
print(f"\n🎉 批量导出完成，共 {total} 个 emoji，用时 {elapsed:.2f} 秒")
