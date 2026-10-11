# hypr-cursortrail

An osu!-style cursor for [Hyprland](https://hyprland.org): a smooth, glowing trail behind the
pointer and a circle cursor that replaces the arrow. Everything is drawn by the compositor with
its own shaders, so it works in every app and follows your colors (e.g. from
[matugen](https://github.com/InioX/matugen)).

![preview](assets/preview.png)

## Features

- **Glowing trail**: a spline through your mouse movement with a solid core and a soft bloom.
  It's drawn every frame at your monitor's refresh rate and stays glued to the cursor.
  - Optional head → tail color gradient, and the trail gets wider the faster you move.
  - Additive (light-like) or normal blending.
  - No spikes on sharp flicks or 180° turns, and round ends.
- **Circle cursor**: a filled circle with a ring, a soft glow and a drop shadow so it stays
  visible on any background. It grows over links/buttons and while a mouse button is held.
- **Styled text cursor**: over text you get an I-beam in the same look, and the trail pauses
  there. Quickly passing over text doesn't count, so the trail doesn't flicker on and off.
- **Game-friendly**: when a game hides or locks the pointer, nothing is drawn and no extra
  frames are scheduled.
- **Configurable**: both the Lua config (Hyprland 0.55+) and the classic `hyprland.conf` work,
  and changes apply live.

## Requirements

- **Hyprland 0.55.x**. Plugins are compiled against one Hyprland version. If you update
  Hyprland, rebuild the plugin (hyprpm and Nix do that for you).
- A C++23 compiler (GCC 14+ or Clang 18+), CMake ≥ 3.27, pkg-config.
- For the circle and text cursor: **software cursors**, `cursor:no_hardware_cursors = 1`.
  With hardware cursors you keep your normal cursor, but the trail still works.

## Installation

### hyprpm (any distro)

```sh
hyprpm update
hyprpm add https://github.com/m-ahiru/hypr-cursortrail
hyprpm enable cursortrail
hyprpm reload
```

Then add `exec-once = hyprpm reload -n` (hyprlang) or the Lua equivalent to your autostart.

### Nix / NixOS

Add the flake and use its **overlay**. It builds the plugin with your own nixpkgs'
`mkHyprlandPlugin`, so it always matches the Hyprland you actually run:

```nix
# flake.nix
inputs.cursortrail.url = "github:m-ahiru/hypr-cursortrail";

# NixOS / Home Manager module
nixpkgs.overlays = [ inputs.cursortrail.overlays.default ];
# → pkgs.hyprlandPlugins.cursortrail
```

Home Manager with the classic config:

```nix
wayland.windowManager.hyprland.plugins = [ pkgs.hyprlandPlugins.cursortrail ];
```

If your Hyprland comes from a **pinned nixpkgs** that differs from your system nixpkgs, build
the plugin from that pin, otherwise the versions won't match:

```nix
let
  hyprPkgs = inputs.nixpkgs-hyprland.legacyPackages.${system};
  cursortrail = hyprPkgs.callPackage "${inputs.cursortrail}/nix" {
    inherit (hyprPkgs.hyprlandPlugins) mkHyprlandPlugin;
  };
in "${cursortrail}/lib/libcursortrail.so"
```

`packages.<system>.default` is built against nixpkgs-unstable's Hyprland and is mostly
useful for CI and testing.

### Manual

You need Hyprland's headers installed (`hyprland.pc` must be found by pkg-config):

```sh
git clone https://github.com/m-ahiru/hypr-cursortrail
cd hypr-cursortrail
make
mkdir -p ~/.local/share/hypr-cursortrail
cp build/libcursortrail.so ~/.local/share/hypr-cursortrail/
```

## Loading and configuration

**Lua config** (`hyprland.lua`, see [`examples/cursortrail.lua`](examples/cursortrail.lua)):

```lua
hl.plugin.load(os.getenv("HOME") .. "/.local/share/hypr-cursortrail/libcursortrail.so")

-- options only exist once the plugin is loaded; skip them on the very first parse
if hl.get_config("plugin.cursortrail.enabled") ~= nil then
    hl.config({ cursor = { no_hardware_cursors = 1 } })
    hl.config({ plugin = { cursortrail = {
        color        = "rgb(ff5800)",
        cursor_color = "rgb(ffe600)",
    } } })
end
```

**Classic config** (`hyprland.conf`, see [`examples/hyprland.conf`](examples/hyprland.conf)):

```ini
plugin = ~/.local/share/hypr-cursortrail/libcursortrail.so

cursor {
    no_hardware_cursors = 1
}

plugin {
    cursortrail {
        color = rgb(ff5800)
        cursor_color = rgb(ffe600)
    }
}
```

Wallpaper colors with matugen: see [`examples/matugen.lua`](examples/matugen.lua).

## Options

All options live under `plugin.cursortrail` (Lua) / `plugin:cursortrail` (hyprlang).
Colors accept any Hyprland color, e.g. `rgb(ff5800)` or `rgba(ff5800ff)`.

### Trail

| option | default | description |
|---|---|---|
| `enabled` | `true` | draw the trail |
| `lifetime` | `175` | how long a point stays, in ms |
| `opacity` | `0.75` | 0–1 |
| `blend` | `additive` | `additive` (glows, adds light) or `normal` (also visible on white) |
| `width` | `8` | core width in px |
| `glow` | `1.0` | glow strength, `0` = off |
| `glow_size` | `4.0` | glow width as a multiple of the core |
| `hot_core` | `0.5` | 0–1, pushes the center towards white |
| `velocity_size` | `true` | faster movement = wider trail |
| `velocity_intensity` | `0.15` | how much speed widens it |
| `color` | `rgb(ff5800)` | head color |
| `gradient` | `false` | fade to `tail_color` along the trail |
| `tail_color` | `rgb(ffd84a)` | tail color |
| `color_boost` | `0` | 0–1, saturates trail and ring colors while keeping the hue (great for pastel matugen colors) |
| `hide_in_fullscreen` | `true` | no trail over fullscreen windows |

### Circle cursor

| option | default | description |
|---|---|---|
| `cursor` | `true` | replace the cursor with the circle |
| `cursor_size` | `11` | outer radius in px |
| `cursor_ring` | `4` | ring thickness |
| `cursor_glow` | `1.0` | glow outside the ring, `0` = off |
| `cursor_glow_size` | `7` | glow reach in px |
| `cursor_shadow` | `0.45` | soft dark halo behind it, for light backgrounds |
| `cursor_shadow_size` | `9` | halo reach in px |
| `cursor_contrast` | `0` | 0–1, an inverted hairline that's visible on literally anything |
| `cursor_outline` | `0` | 0–1, hard dark edge |
| `cursor_hover_scale` | `1.25` | size over links / buttons |
| `cursor_click_scale` | `1.2` | size while a mouse button is held |
| `cursor_color` | `rgb(ffe600)` | ring and glow |
| `cursor_center_color` | `rgb(ffffff)` | filled center |
| `cursor_in_fullscreen` | `true` | keep the circle over fullscreen windows |

### Text cursor

| option | default | description |
|---|---|---|
| `cursor_keep_text` | `true` | over text: show an I-beam and pause the trail (`false` = circle everywhere) |
| `cursor_text_delay` | `200` | ms the pointer has to stay over text before that kicks in |
| `cursor_text_style` | `true` | draw the I-beam in the circle's style (`false` = your theme's I-beam) |
| `cursor_text_height` | `20` | I-beam height in px |
| `cursor_text_width` | `5` | I-beam thickness in px |

## FAQ

**Can I get banned by anti-cheat?**
The plugin runs inside Hyprland, not inside the game. It doesn't touch game memory or input; it
only reads the pointer position the compositor already has and draws on top of the final image,
like Hyprland's own borders and animations. No guarantees, but there's nothing for a
game-side anti-cheat to see.

**Some apps/games still show their own cursor.**
Games often hide the system cursor and draw their own inside the game. That's part of the
game's image and can't be replaced by the compositor. Terminals show the text cursor almost
everywhere; set `cursor_keep_text = false` if you want the circle there too.

**The circle doesn't show up.**
It needs `cursor:no_hardware_cursors = 1`. Also check `hyprctl plugin list` and the Hyprland
log for `[cursortrail]` messages.

**It stopped working after a Hyprland update.**
Rebuild the plugin against the new version (`hyprpm update`, or rebuild your Nix config). If
Hyprland's plugin API changed, the plugin needs an update. Open an issue with your
`hyprctl version`.

## How it works

- **Trail**: the mouse positions are thinned out and smoothed, then turned into a centripetal
  Catmull-Rom spline. The tail end is clipped exactly at its lifetime, so it retracts smoothly.
  For drawing, the spline is resampled to ≤ 64 points and sent as a uniform array. A single
  quad over the trail's bounding box computes, per pixel, the distance to every segment and
  keeps the **maximum** contribution. That's why folds and self-crossings never double up or
  spike.
- **Cursor**: Hyprland draws software cursors as a texture pass element. The plugin finds that
  element in the frame's render pass and swaps in its own shader-drawn cursor at the same
  position, so the cursor stays on top of the trail. The current cursor shape (arrow, link,
  text, app-supplied image) is tracked by hooking `CCursorManager::setCursorFromName` and
  `setCursorSurface`.

## Building against a new Hyprland version

1. `hyprpm update` / update your flake inputs.
2. `make`. If it fails, the plugin API changed. The Hyprland calls are in `src/Trail.cpp`
   (render pass, pointer, renderer) and `src/main.cpp` (config, events, hooks).
3. After pushing a fix, add a pin to `hyprpm.toml`: `["<hyprland commit>", "<this repo's commit>"]`.

## License

[MIT](LICENSE)
