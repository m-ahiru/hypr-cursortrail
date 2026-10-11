{
  description = "osu!-style glowing cursor trail and circle cursor for Hyprland";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      inherit (nixpkgs) lib;
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      eachSystem = lib.genAttrs systems;
      pkgsFor = eachSystem (
        system:
        import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        }
      );
    in
    {
      # Adds `hyprlandPlugins.cursortrail` to your pkgs. Because it's built with your pkgs'
      # mkHyprlandPlugin, it matches the Hyprland from those pkgs - use this one.
      overlays.default = final: prev: {
        hyprlandPlugins = (prev.hyprlandPlugins or { }) // {
          cursortrail = final.callPackage ./nix {
            inherit (final.hyprlandPlugins) mkHyprlandPlugin;
          };
        };
      };

      # Built against nixpkgs-unstable's Hyprland. Only matches if you run that exact Hyprland.
      packages = eachSystem (system: {
        cursortrail = pkgsFor.${system}.hyprlandPlugins.cursortrail;
        default = self.packages.${system}.cursortrail;
      });

      checks = eachSystem (system: {
        build = self.packages.${system}.cursortrail;
      });

      devShells = eachSystem (
        system:
        let
          pkgs = pkgsFor.${system};
        in
        {
          default = pkgs.mkShell {
            inputsFrom = [ pkgs.hyprlandPlugins.cursortrail ];
            packages = [ pkgs.clang-tools ];
          };
        }
      );
    };
}
