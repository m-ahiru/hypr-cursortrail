"""Render every cursor_style with the plugin's real shaders.

usage: python3 tools/render-styles.py src/Shaders.hpp assets/cursor-styles.png [scale]
needs: numpy, pillow, moderngl (EGL), the Inter font
"""
import re, sys
import numpy as np, moderngl
from PIL import Image, ImageDraw, ImageFont

SH, OUT = sys.argv[1:3]
SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 4.0

txt = open(SH).read()
G = lambda n: re.search(n + r' = R"glsl\((.*?)\)glsl"', txt, re.S).group(1)
fix = lambda s: s.replace('#version 300 es', '#version 330')
VERT = fix(G('CURSORCIRCLE_VERT'))
FRAG = fix(G('CURSORSHAPE_LIB') + G('CURSORCIRCLE_FRAG'))
XFRAG = fix(G('CURSORSHAPE_LIB') + G('CURSORCONTRAST_FRAG'))

NAMES = ["classic", "ring", "solid", "ring + dot", "double ring", "bullseye", "dashed", "split",
         "crosshair", "orb", "diamond", "hexagon", "square", "star", "scope", "dot"]

# plugin defaults (logical px)
CFG = dict(size=11, ring=4, glow=1.0, glow_size=7, shadow=0.45, shadow_size=9, outline=0.0, contrast=0.0,
           color=0xFFE600, center=0xFFFFFF)

COLS, TILE, LABEL = 8, 150, 34
ROWS = (len(NAMES) + COLS - 1) // COLS
W, H = COLS * TILE, ROWS * (TILE + LABEL)

def hexcol(c):
    return ((c >> 16 & 255) / 255, (c >> 8 & 255) / 255, (c & 255) / 255)

def lin(c):  # the plugin hands sRGB values straight to GL; keep that
    return c

# background: dark tiles with a subtle vertical gradient, like a wallpaper
bg = Image.new('RGB', (W, H), (17, 17, 27))
d = ImageDraw.Draw(bg)
for r in range(ROWS):
    for c in range(COLS):
        x0, y0 = c * TILE, r * (TILE + LABEL)
        for yy in range(TILE):
            k = yy / TILE
            col = (int(30 + 10 * k), int(30 + 8 * k), int(46 + 12 * k))
            d.line([(x0 + 6, y0 + 6 + yy * (TILE - 12) / TILE), (x0 + TILE - 7, y0 + 6 + yy * (TILE - 12) / TILE)], fill=col)

ctx = moderngl.create_standalone_context(backend='egl')
screen = ctx.simple_framebuffer((W, H), components=4)
screen.use()
tex = ctx.texture((W, H), 4, bg.convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM).tobytes())
tex.use(0)
blit = ctx.program(vertex_shader='#version 330\nin vec2 p;out vec2 uv;void main(){uv=p*0.5+0.5;gl_Position=vec4(p,0,1);}',
                   fragment_shader='#version 330\nuniform sampler2D t;in vec2 uv;out vec4 c;void main(){c=texture(t,uv);}')
ctx.vertex_array(blit, [(ctx.buffer(np.array([-1, -1, 1, -1, -1, 1, 1, 1], dtype='f4')), '2f', 'p')]).render(moderngl.TRIANGLE_STRIP)

prog = ctx.program(vertex_shader=VERT, fragment_shader=FRAG)
xprog = ctx.program(vertex_shader=VERT, fragment_shader=XFRAG)
proj = np.array([2, 0, -1, 0, -2, 1, 0, 0, 1], dtype='f4').reshape(3, 3).T.copy().tobytes()

def setu(p, name, val):
    if name in p:
        p[name] = val

for p in (prog, xprog):
    p['uProj'].write(proj)
    p['uFullSize'] = (W, H)

ctx.enable(moderngl.BLEND)
s = SCALE
radius, ring = CFG['size'] * s, CFG['ring'] * s
glow_size, shadow_size = CFG['glow_size'] * s, CFG['shadow_size'] * s
outer = radius + max(glow_size, shadow_size, 3 * s) + 2 * s

for i, name in enumerate(NAMES):
    r, c = divmod(i, COLS)
    cx, cy = c * TILE + TILE / 2, r * (TILE + LABEL) + TILE / 2
    h = outer
    q = np.array([cx - h, cy - h, -1, -1, cx + h, cy - h, 1, -1, cx - h, cy + h, -1, 1, cx + h, cy + h, 1, 1], dtype='f4')
    vb = ctx.buffer(q.tobytes())
    setu(prog, 'uColor', lin(hexcol(CFG['color'])))
    setu(prog, 'uCenterColor', lin(hexcol(CFG['center'])))
    setu(prog, 'uOuter', h)
    setu(prog, 'uRadius', radius)
    setu(prog, 'uRing', ring)
    setu(prog, 'uGlow', CFG['glow'])
    setu(prog, 'uGlowSize', glow_size)
    setu(prog, 'uOutline', CFG['outline'])
    setu(prog, 'uShadow', CFG['shadow'])
    setu(prog, 'uShadowSize', shadow_size)
    setu(prog, 'uStyle', i)
    ctx.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)
    ctx.vertex_array(prog, [(vb, '2f 2f', 'aPos', 'aData')]).render(moderngl.TRIANGLE_STRIP)
    if CFG['contrast'] > 0:
        setu(xprog, 'uOuter', h); setu(xprog, 'uRadius', radius); setu(xprog, 'uRing', ring)
        setu(xprog, 'uContrast', CFG['contrast']); setu(xprog, 'uStyle', i)
        ctx.blend_func = (moderngl.ONE_MINUS_DST_COLOR, moderngl.ONE_MINUS_SRC_ALPHA)
        ctx.vertex_array(xprog, [(vb, '2f 2f', 'aPos', 'aData')]).render(moderngl.TRIANGLE_STRIP)

img = Image.frombytes('RGBA', (W, H), screen.read(components=4)).transpose(Image.FLIP_TOP_BOTTOM).convert('RGB')

# labels: big number, small name
d = ImageDraw.Draw(img)
fnum = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Bold.otf', 22)
fname = ImageFont.truetype('/usr/share/fonts/opentype/inter/Inter-Regular.otf', 13)
for i, name in enumerate(NAMES):
    r, c = divmod(i, COLS)
    x0, y0 = c * TILE, r * (TILE + LABEL) + TILE
    num = str(i)
    nw = d.textlength(num, font=fnum)
    gap = 7
    tw = nw + gap + d.textlength(name, font=fname)
    sx = x0 + (TILE - tw) / 2
    d.text((sx, y0 - 2), num, font=fnum, fill=(235, 235, 245))
    d.text((sx + nw + gap, y0 + 6), name, font=fname, fill=(150, 150, 170))

img.save(OUT, optimize=True)
print('ok', img.size)
