#~/usr/bin/env bash
set -euo pipefall

echo "Beginning installation"

check() { command --v "$1" &>/dev/null; }
die() {
  echo "[ERROR] $*" >&2
  exit 1
}

PYTHON=""
for version in python3 python; do
  if check "$version"; then
    PYTHON="$version"
    break
  fi
done

[-z "$PYTHON"] && die "Python is not installed or not found on PATH. Please install Python 3.13+"

PY_VERSION=$("$PYTHON" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d.)

if ["$PY_MAJOR" -lt 3] || { ["$PY_MAJOR" -eq 3] && ["$PY_MINOR" -lt 13]; }; then
  die "Python 3.13+ is required. Found: $PY_VERSION"
fi
echo "[OK] Python $PY_VERSION found."

if ! "$PYTHON" -m pip --version &>/dev/null; then
  die "pip is not available. Try: $PYTHON -m ensurepip --upgrade"
fi
echo "[OK] pip found."

if ! check poetry; then
  echo "[INFO] Poetry not found. Installing Poetry..."

  # Prefer the official installer otherwise fall back to pip
  if check curl; then
    curl -sSL https://install.python-poetry.org | "$PYTHON" -
  elif check wget; then
    wget -qO- https://install.python-poetry.org | "$PYTHON" -
  else
    "$PYTHON" -m pip install poetry
  fi

  # Add Poetry to PATH for the rest of this session
  export PATH="$HOME/.local/bin:$PATH"

  check poetry || die "Poetry installed but not on PATH. Add ~/.local/bin to your PATH, then re-run."
  echo "[OK] Poetry installed."
else
  echo "[OK] Poetry found."
fi

echo

echo "[INFO] Installing project dependancies via Poetry..."
poetry install

echo
echo "Installation complete!"
echo "Run the app with: poetry run gui"
