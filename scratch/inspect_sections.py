import urllib.request, re

req = urllib.request.Request('https://hanzo.framer.website/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Extract CSS variables / tokens
tokens = re.findall(r'(--[a-zA-Z0-9_-]+:\s*[^;]+;)', html)
print(f"Total tokens found: {len(tokens)}")
for t in tokens[:35]:
    print(" ", t)

# Extract body styles or root styles
root_styles = re.findall(r'body\{([^}]+)\}', html)
for r in root_styles[:3]:
    print("\nBody style:", r[:200])

# Inspect sections and their layout (flex / grid / max-width / alignment)
main_containers = re.findall(r'(\.framer-[a-zA-Z0-9]+\s*\{[^}]*max-width[^}]*\})', html)
for c in main_containers[:10]:
    print("\nContainer:", c)

# Let's inspect the actual content sections:
# Find all visible headings (h1, h2, h3, or text blocks)
headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', html, flags=re.DOTALL)
print("\nHEADINGS:")
for h in headings:
    clean_h = re.sub(r'<[^>]+>', '', h).strip()
    if clean_h:
        print("  -", clean_h)
