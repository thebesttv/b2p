# nix develop --extra-experimental-features nix-command --extra-experimental-features flakes

{
  description = "b2p";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-24.05";
  };

  outputs = { self, nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs {
        inherit system;
      };

      # Define a common set of dependencies, using 'with pkgs' to simplify
      dependencies = with pkgs; [
        figlet
        php
        python312
        python312Packages.tqdm
        python312Packages.pyaml
      ];
    in {
      packages = {
        default = pkgs.mkShell {
          buildInputs = dependencies;
        };
      };

      # Define a Docker image
      dockerImage = pkgs.dockerTools.buildImage {
        name = "b2p";
        tag = "latest";
        contents = dependencies;
      };
    };
}
        # (callPackage ./bbdown.nix { ffmpeg = ffmpeg_7-headless; })
