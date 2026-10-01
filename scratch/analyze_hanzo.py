import urllib.request
import re
from collections import Counter

req = urllib.request.Request('https://hanzo.framer.website/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# 1. Colors
hex_colors = [c.upper() for c in re.findall(r'#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3}', html)]
color_counts = Counter(hex_colors)
print("TOP HEX COLORS:")
for c, cnt in color_counts.most_common(20):
    print(f"  {c}: {cnt}")

# 2. Font sizes & line heights
font_sizes = re.findall(r'font-size:\s*([^;]+);', html)
fs_counts = Counter(font_sizes)
print("\nFONT SIZES:")
for fs, cnt in fs_counts.most_common(15):
    print(f"  {fs}: {cnt}")

# 3. Font families & weights
font_families = re.findall(r'font-family:\s*([^;]+);', html)
ff_counts = Counter(font_families)
print("\nFONT FAMILIES:")
for ff, cnt in ff_counts.most_common(10):
    print(f"  {ff}: {cnt}")

font_weights = re.findall(r'font-weight:\s*([^;]+);', html)
fw_counts = Counter(font_weights)
print("\nFONT WEIGHTS:")
for fw, cnt in fw_counts.most_common(10):
    print(f"  {fw}: {cnt}")

# 4. Spacing / gaps / padding
paddings = re.findall(r'padding:\s*([^;]+);', html)
p_counts = Counter(paddings)
print("\nPADDINGS:")
for p, cnt in p_counts.most_common(10):
    print(f"  {p}: {cnt}")

gaps = re.findall(r'gap:\s*([^;]+);', html)
gap_counts = Counter(gaps)
print("\nGAPS:")
for g, cnt in gap_counts.most_common(10):
    print(f"  {g}: {cnt}")

# 5. Framer sections
names = re.findall(r'data-framer-name="([^"]+)"', html)
print("\nFRAMER COMPONENT NAMES (unique):")
print(set(names))
