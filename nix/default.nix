# Package definition. Built with mkHyprlandPlugin so it always compiles against the
# Hyprland of the nixpkgs instance it's called from - i.e. the Hyprland you actually run.
{
  lib,
  cmake,
  mkHyprlandPlugin,
}:
mkHyprlandPlugin {
  pluginName = "cursortrail";
  version = "1.0.0";

  src = lib.cleanSource ../.;

  nativeBuildInputs = [ cmake ];

  meta = {
    description = "osu!-style glowing cursor trail and circle cursor for Hyprland";
    homepage = "https://github.com/m-ahiru/hypr-cursortrail";
    license = lib.licenses.mit;
    platforms = lib.platforms.linux;
  };
}
