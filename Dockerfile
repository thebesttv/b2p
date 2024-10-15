# Use a lightweight NixOS image
FROM nixos/nix

# Copy the flake file into the container
COPY flake.nix /app/flake.nix

# Install Nix flakes and dependencies
RUN nix-env -iA nixpkgs.nixFlakes && \
    nix shell --command true

# Set working directory
WORKDIR /app

# Copy the rest of the application (Python code, etc.)
COPY . /app

# Build the Docker image with dependencies using flake
RUN nix build .#dockerImage

# Command to run the Python script
CMD ["python3", "main.py", "/app/config.yaml"]
