{pkgs}:
pkgs.mkShellNoCC {
  # resolve dynamic library paths
  LD_LIBRARY_PATH = "${(with pkgs;
    lib.makeLibraryPath [
      zlib
      zstd
      stdenv.cc.cc
      curl
      openssl
      attr
      libssh
      bzip2
      libxml2
      acl
      libsodium
      util-linux
      xz
      systemd
      glib.out
    ])}:${pkgs.libGL}/lib"; # libGL don't work for makeLibraryPath
  preferLocalBuild = true;
  packages = with pkgs; [
    uv
    alejandra

    # aliases
    (writeShellScriptBin "py3" "uv run python")
    (writeShellScriptBin "py" "uv run python")
    (writeShellScriptBin "python" "uv run python")
    (writeShellScriptBin "python3" "uv run python")
    (writeShellScriptBin "black" "uv run black .")
    (writeShellScriptBin "pytest" "uv run pytest .")
    (writeShellScriptBin "isort" "uv run isort .")
  ];

  shellHook = ''
    python --version
    uv sync
    alejandra .
  '';
}
