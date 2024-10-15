# Use a lightweight NixOS image
FROM nixos/nix

# Enable nix-command and flakes experimental features
RUN mkdir -p /etc/nix && echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

# Copy the flake file into the container
COPY flake.nix /app/flake.nix

# Set working directory
WORKDIR /app

# Install dependencies using flake
RUN nix build .#dockerImage --extra-experimental-features nix-command --extra-experimental-features flakes

# Copy the rest of the application (Python code, etc.)
COPY . /app

# Command to run the Python script
# CMD ["sh", "-c", "figlet b2p! && python3 main.py /app/config.yaml"]
