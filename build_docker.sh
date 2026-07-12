#!/usr/bin/env bash
# Installs Docker if missing, then builds the app image(s).
# After this finishes, run: sudo docker compose up -d
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -f "backend/.env" ]; then
  echo "Missing backend/.env — copy backend/.env.example to backend/.env and set your GEMINI_API_KEY first."
  exit 1
fi

OS_NAME="$(uname -s)"

if ! command -v docker >/dev/null; then
  if [ "$OS_NAME" = "Darwin" ]; then
    echo "Docker not found — installing Docker Desktop..."
    if ! command -v brew >/dev/null; then
      echo "Homebrew is required to auto-install Docker Desktop on Mac."
      echo "Install Homebrew first: https://brew.sh"
      echo "Or install Docker Desktop manually: https://www.docker.com/products/docker-desktop/"
      exit 1
    fi
    brew install --cask docker
    echo "Docker Desktop installed. Open it once from Applications/Spotlight so it finishes"
    echo "first-time setup (whale icon appears in the menu bar), then re-run this script."
    exit 1
  fi

  echo "Docker not found — installing (requires sudo)..."
  sudo install -m 0755 -d /etc/apt/keyrings
  curl -fsSL "https://download.docker.com/linux/ubuntu/gpg" -o /tmp/docker.asc
  sudo mv /tmp/docker.asc /etc/apt/keyrings/docker.asc
  sudo chmod a+r /etc/apt/keyrings/docker.asc
  ARCH="$(dpkg --print-architecture)"
  CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
  echo "deb [arch=$ARCH signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $CODENAME stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
  sudo apt-get update -qq
  # Installs only what we need — skips optional extras (e.g. docker-model-plugin)
  # that aren't packaged for older/EOL Ubuntu releases and would abort the install.
  sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
  sudo usermod -aG docker "$USER"
  echo "Docker installed. Log out/in (or run 'newgrp docker') for group permissions to apply."
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose plugin not found. Install it with: sudo apt-get install docker-compose-plugin"
  exit 1
fi

# On Linux, the docker socket is usually only accessible via sudo unless the
# current user is in the "docker" group (which only takes effect after a
# fresh login) — Mac's Docker Desktop never needs sudo.
if [ "$OS_NAME" != "Darwin" ] && ! docker info >/dev/null 2>&1; then
  DOCKER_CMD="sudo docker"
else
  DOCKER_CMD="docker"
fi

echo "Building images..."
$DOCKER_CMD compose build

echo ""
echo "Build complete. Start the app with:"
if [ "$DOCKER_CMD" = "sudo docker" ]; then
  echo "  sudo docker compose up -d"
else
  echo "  docker compose up -d"
fi
echo "Then open http://localhost:8000"
