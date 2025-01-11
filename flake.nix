# nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

{
  description = "b2p";

  inputs = {
    # 需要使用 ffmpeg 7.0.1 或 7.0.2，否则生成的 sha256 不匹配
    nixpkgs.url = "github:NixOS/nixpkgs/05bbf675397d5366259409139039af8077d695ce";
  };

  outputs = { self , nixpkgs , ... }: let
    # system should match the system you are running on
    system = "x86_64-linux";
  in {
    devShells."${system}".default = let
      pkgs = import nixpkgs {
        inherit system;
      };
      bbdown = with pkgs; (
        callPackage ./bbdown.nix { ffmpeg = ffmpeg_7-headless; }
      );
    in pkgs.mkShell {
      packages = with pkgs; [
        # display banner
        figlet

        # main.py
        python312
        python312Packages.tqdm
        python312Packages.pyyaml

        # dir2cast
        php

        bbdown
      ];

      shellHook = ''
        figlet b2p!
      '';
    };
  };
}
