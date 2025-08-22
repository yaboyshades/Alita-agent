#!/usr/bin/env bash
set -euo pipefail

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setting up VS Code extension..."
pushd cortex-extension >/dev/null
npm install
npm run compile
popd >/dev/null

echo "Installing pre-commit and hooks..."
pip install pre-commit
pre-commit install

echo "✅ Setup complete!"
echo "Run the proxy: python run_proxy.py"
echo "Then reload VS Code and use Cortex commands"
