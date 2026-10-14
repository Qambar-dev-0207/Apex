# APEX Mascot Assets

Transparent PNG crops extracted from the APEX mascot reference sheet supplied in the conversation. Each pose is an individual asset; do not use the full source sheet as a single website image.

## Assets

- `apex-mascot-hero.png` — primary mascot / brand anchor
- `apex-mascot-focus.png` — focus mode
- `apex-mascot-coding.png` — coding; includes laptop
- `apex-mascot-thinking.png` — thinking; includes thought bubble
- `apex-mascot-learning.png` — learning; includes book
- `apex-mascot-building.png` — building; includes wrench and blocks
- `apex-mascot-analyzing.png` — analyzing; includes chart panel
- `apex-mascot-deploying.png` — deploying; includes rocket
- `apex-mascot-connected.png` — connected; includes signal icon
- `apex-mascot-happy.png` — happy expression
- `apex-mascot-excited.png` — excited expression
- `apex-mascot-focused.png` — focused expression
- `apex-mascot-determined.png` — determined expression
- `apex-mascot-curious.png` — curious expression; includes question mark
- `apex-mascot-proud.png` — proud expression

## Integration notes

- These are transparent RGBA PNGs. Copy them into the existing project's local public assets directory, for example `public/images/mascots/`.
- Preserve aspect ratio; use `object-fit: contain`.
- Keep the character art tasteful and secondary to APEX's cinematic dark visual system. Do not place all poses in a large gallery.
- Use only a few action poses in relevant sections. Emotion poses are best used as small state feedback, not random decoration.
- Keep source dimensions/known aspect ratios reserved to avoid layout shift and provide meaningful alt text only when the mascot conveys information. Use empty alt text if decorative.
