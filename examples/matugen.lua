-- Follow your wallpaper with matugen (https://github.com/InioX/matugen).
--
-- 1. matugen template (e.g. ~/.config/matugen/templates/hyprland-colors.lua):
--
--      return {
--          primary   = "rgb({{colors.primary.default.hex_stripped}})",
--          secondary = "rgb({{colors.secondary.default.hex_stripped}})",
--          tertiary  = "rgb({{colors.tertiary.default.hex_stripped}})",
--      }
--
-- 2. matugen config.toml:
--
--      [templates.hyprland]
--      input_path  = '~/.config/matugen/templates/hyprland-colors.lua'
--      output_path = '~/.config/hypr/colors.lua'
--      post_hook   = "hyprctl reload"
--
-- 3. in your cursortrail config:

local ok, colors = pcall(require, "colors")
if not ok or type(colors) ~= "table" then colors = {} end

hl.config({
    plugin = {
        cursortrail = {
            cursor_color = colors.primary  or "rgb(ff5800)",  -- circle in one role...
            color        = colors.tertiary or "rgb(ffd84a)",  -- ...trail in another
            tail_color   = colors.secondary or "rgb(ff8a00)",
            gradient     = true,
            color_boost  = 0.6, -- matugen's dark-mode colors are pastel; this makes them pop
        },
    },
})
