"""Test icon loading."""
import io

from PIL import Image
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

# Get path to SVG icon
svg_path = "assets/icon.svg"

# Convert SVG to reportlab drawing
drawing = svg2rlg(svg_path)

# Render to PNG in memory at menu bar size (44x44 for @2x)
png_data = io.BytesIO()
renderPM.drawToFile(drawing, png_data, fmt='PNG', dpi=72, bg=0x00000000)
png_data.seek(0)

# Load as PIL Image and resize to exact dimensions
image = Image.open(png_data)
image = image.resize((44, 44), Image.Resampling.LANCZOS)

# Convert to RGBA to ensure transparency
if image.mode != 'RGBA':
    image = image.convert('RGBA')

print(f"Icon loaded successfully: {image.size}, mode: {image.mode}")
image.save("/tmp/test_icon.png")
print("Saved to /tmp/test_icon.png")
