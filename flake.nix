# nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

{
  description = "b2p";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = { self , nixpkgs , ... }: let
    # system should match the system you are running on
    system = "x86_64-linux";
  in {
    devShells."${system}".default = let
      pkgs = import nixpkgs {
        inherit system;
      };
    in pkgs.mkShell {
      packages = with pkgs; [
        figlet

        python312
        python312Packages.tqdm
        python312Packages.pyyaml

        php

        (callPackage ./bbdown.nix { ffmpeg = ffmpeg_7-headless; })
      ];

      shellHook = ''
        figlet b2p!
      '';
    };
  };
}
