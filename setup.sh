#!/bin/bash
# ============================================================
#  Cyberdeck Setup — One-click installer for Linux/macOS
#  Installs the Cyberdeck skill into Hermes Agent
# ============================================================

set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║     CYBERDECK v5.0 — Setup Wizard        ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

# Check Hermes
if ! command -v hermes &>/dev/null; then
    echo "[FAIL] Hermes Agent not found."
    echo "       Install from: https://github.com/NousResearch/hermes-agent"
    exit 1
fi
echo "[OK]   Hermes Agent found"

# Install skill
SKILL_DIR="$HOME/.hermes/skills/software-development/cyberdeck"
mkdir -p "$SKILL_DIR"
cp "$(dirname "$0")/SKILL.md" "$SKILL_DIR/SKILL.md"
echo "[OK]   SKILL.md installed to $SKILL_DIR"

# Check .env
if [ -f "$HOME/.hermes/.env" ]; then
    if grep -q "API_KEY" "$HOME/.hermes/.env" 2>/dev/null; then
        echo "[OK]   API keys found in .env"
    else
        echo "[WARN] No API keys in .env"
    fi
else
    echo "[WARN] No .env found. Copy .env.example, add your keys."
fi

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   INSTALL COMPLETE                       ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""
echo "  Next:  hermes -s cyberdeck"
echo "         (then just chat — wizard auto-runs)"
echo ""
echo "  Demo:  python3 mini-agent.py 'Hello!'"
echo ""
