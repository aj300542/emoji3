from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import svgwrite
import json
import os

# ✅ 参数设置
FONT_PATH = r"Z:/2025/emoji135/font/seguiemj-1.35-flat.ttf"
EMOJI_CHAR = "🫦"
OUTPUT_DIR = "emoji_layers"
SIZE = 256  # SVG 尺寸
JSON_FILENAME = "emoji_layers_metadata.json"

# ✅ 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ✅ 加载字体
font = TTFont(FONT_PATH)
glyph_set = font.getGlyphSet()
cmap = font.getBestCmap()

# ✅ 检查是否支持 COLR/CPAL
if "COLR" not in font or "CPAL" not in font:
    raise ValueError("该字体不支持 COLR/CPAL 彩色图层结构")

colr = font["COLR"]
cpal = font["CPAL"]

# ✅ 获取 emoji 对应的 glyph name
base_glyph = cmap.get(ord(EMOJI_CHAR))
if not base_glyph:
    raise ValueError("找不到该 emoji 的 glyph")

# ✅ 获取图层信息
layers = colr.ColorLayers[base_glyph]
palette = cpal.palettes[0]  # 使用第一个调色板

# ✅ 图层元信息列表
layer_metadata = []

# ✅ 遍历每个图层并导出为独立 SVG
for i, layer in enumerate(layers):
    glyph_name = layer.name
    color_index = layer.colorID
    bgra = palette[color_index]

    # ✅ 修正颜色顺序：BGRA → RGBA
    b, g, r = bgra[:3]
    r = r if isinstance(r, int) else 0
    g = g if isinstance(g, int) else 0
    b = b if isinstance(b, int) else 0

    # ✅ 转换为十六进制颜色字符串
    hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)

    # ✅ 提取路径
    pen = SVGPathPen(glyph_set)
    glyph_set[glyph_name].draw(pen)
    path_data = pen.getCommands()

    # ✅ 创建 SVG 文件
    svg_filename = f"emoji_layer_{i:02d}.svg"
    svg_path = os.path.join(OUTPUT_DIR, svg_filename)
    dwg = svgwrite.Drawing(svg_path, size=(SIZE, SIZE))
    dwg.add(dwg.path(
        d=path_data,
        style=f"fill:{hex_color};stroke:none",
        transform=f"scale(1,-1) translate(0,-{SIZE})"
    ))
    dwg.save()
    print(f"✅ 已保存图层 {i} 到: {svg_path}，颜色: {hex_color}")

    # ✅ 添加图层元信息
    layer_metadata.append({
        "layer_index": i,
        "glyph_name": glyph_name,
        "color": {"r": r, "g": g, "b": b},
        "hex": hex_color,
        "svg_file": svg_filename
    })

# ✅ 保存 JSON 文件（添加 emoji 信息）
json_path = os.path.join(OUTPUT_DIR, JSON_FILENAME)
emoji_code = f"U+{ord(EMOJI_CHAR):04X}"

output_data = {
    "emoji_char": EMOJI_CHAR,
    "emoji_code": emoji_code,
    "layers": layer_metadata
}

with open(json_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=2)
print(f"📄 已保存图层元信息到: {json_path}，emoji: {EMOJI_CHAR} ({emoji_code})")
