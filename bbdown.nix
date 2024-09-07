# https://github.com/CrackTC/nur-packages/blob/b4ad20eaefbd5aca48d979aaca4c5406acc95e0e/pkgs/bbdown/default.nix

{ lib
, buildDotnetGlobalTool
, dotnetCorePackages
, ffmpeg
}:

let
  pname = "BBDown";
  version = "1.6.3";
  dotnet-sdk = dotnetCorePackages.sdk_8_0;
  dotnet-runtime = dotnet-sdk;
  bbdown = buildDotnetGlobalTool
    {
      inherit pname version dotnet-runtime dotnet-sdk;
      nugetSha256 = "sha256-dxsFriDIXNR8POAOFOraXBNDWI5PnxHpDpZM3JQJOzg=";

      meta = with lib; {
        description = "Bilibili Downloader";
        homepage = "https://github.com/nilaoda/BBDown";
        license = licenses.mit;
        mainProgram = pname;
        platforms = platforms.linux;
      };
    };
in
bbdown.overrideAttrs (attrs: {
  postFixup = ''
    wrapProgram $out/bin/${pname} \
      --prefix PATH : "${lib.makeBinPath [ ffmpeg ]}"
  '';
})
