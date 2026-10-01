import urllib.request, re

req = urllib.request.Request('https://hanzo.framer.website/', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# 1. Structure of sections
print("--- SECTIONS / BLOCKS ---")
sections = re.findall(r'<section[^>]*>(.*?)</section>', html, flags=re.DOTALL)
print(f"Total <section> tags: {len(sections)}")

# If framer doesn't use semantic <section>, let's find main containers
div_names = re.findall(r'data-framer-name="([^"]+)"', html)
# Let's see top-level framer names
top_level = []
seen = set()
for name in div_names:
    if name not in seen:
        seen.add(name)
        top_level.append(name)
print("Top Framer Component names:", top_level[:40])

# Let's inspect the actual text flow in order of appearance
clean_text = re.sub(r'<script.*?</script>', '', html, flags=re.DOTALL)
clean_text = re.sub(r'<style.*?</style>', '', clean_text, flags=re.DOTALL)
snippets = re.findall(r'>([^<]{2,})<', clean_text)
ordered_snippets = []
for s in snippets:
    s_strip = s.strip()
    if s_strip and not s_strip.startswith('{') and not s_strip.startswith('var') and len(s_strip) > 1:
        if not ordered_snippets or ordered_snippets[-1] != s_strip:
            ordered_snippets.append(s_strip)

print(f"\nTotal ordered text snippets: {len(ordered_snippets)}")
for i, s in enumerate(ordered_snippets[:50]):
    print(f"{i+1}: {s}")
