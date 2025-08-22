"""Test package configuration for Alita Agent."""

from pathlib import Path
import sys

# Ensure the alita_agent package is importable when tests are run from the
# repository root. This mirrors the behaviour of installing the project but
# avoids requiring a separate installation step during CI.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
