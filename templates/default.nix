# Initialise with `nix flake init -t git+ssh://git@github.com/${username}/${private-repo}

# github:UWA-Medical-Physics-Research-Group/turtwig#template-name
# files at `path` are copied when initialising flake
{
  python312 = {
    path = ./python312;
    description = "Starter template for Python 3.12.7 using uv";
  };
}
