-- Example config for Hyprland's Lua config (0.55+).
-- Put it next to your hyprland.lua and add  require("cursortrail")  to it.

-- 1. load the plugin (adjust the path; hyprpm users can skip this, `hyprpm reload` loads it)
hl.plugin.load(os.getenv("HOME") .. "/.local/share/hypr-cursortrail/libcursortrail.so")

-- The plugin registers its options when it loads, right after this file is parsed the
-- first time. Only set them once they exist, so the first parse doesn't complain.
if hl.get_config("plugin.cursortrail.enabled") == nil then
    return
end

-- 2. the circle cursor needs software cursors
hl.config({ cursor = { no_hardware_cursors = 1 } })

-- 3. options (all optional, these are the defaults unless noted)
hl.config({
    plugin = {
        cursortrail = {
            -- trail
            enabled            = true,
            lifetime           = 175,           -- ms
            opacity            = 0.75,
            blend              = "additive",    -- "additive" (glow) | "normal" (also visible on white)
            width              = 8,
            glow               = 1.0,
            glow_size          = 4.0,
            hot_core           = 0.5,
            velocity_size      = true,
            velocity_intensity = 0.15,
            color              = "rgb(ff5800)",
            gradient           = true,          -- default: false
            tail_color         = "rgb(ffd84a)",
            color_boost        = 0,             -- 0..1, saturate pastel (e.g. matugen) colors
            hide_in_fullscreen = false,         -- default: true

            -- circle cursor
            cursor              = true,
            cursor_style        = 0,            -- 0..15, see the README
            cursor_size         = 11,
            cursor_ring         = 4,
            cursor_glow         = 1.0,
            cursor_glow_size    = 7,
            cursor_shadow       = 0.45,
            cursor_shadow_size  = 9,
            cursor_contrast     = 0,
            cursor_outline      = 0,
            cursor_hover_scale  = 1.25,
            cursor_click_scale  = 1.2,
            cursor_color        = "rgb(ffe600)",
            cursor_center_color = "rgb(ffffff)",
            cursor_in_fullscreen = true,

            -- text cursor
            cursor_keep_text    = true,
            cursor_text_delay   = 200,
            cursor_text_style   = true,
            cursor_text_height  = 20,
            cursor_text_width   = 5,
        },
    },
})
