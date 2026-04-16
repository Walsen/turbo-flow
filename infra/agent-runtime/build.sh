#!/usr/bin/env bash
# =============================================================================
# Build the AgentCore deployment package.
#
# Bundles main.py + turboflow_adapter into a deployable structure
# that the agentcore CLI can deploy.
#
# Usage:
#   cd infra/agent-runtime
#   bash build.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ADAPTER_SRC="$REPO_ROOT/agent-adapter/python/turboflow_adapter"
BUILD_DIR="$SCRIPT_DIR/build"

echo "Building AgentCore deployment package..."

# Clean
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/lib"

# Copy runtime entry point
cp "$SCRIPT_DIR/main.py" "$BUILD_DIR/main.py"
cp "$SCRIPT_DIR/requirements.txt" "$BUILD_DIR/requirements.txt"

# Copy turboflow_adapter as a library
cp -r "$ADAPTER_SRC" "$BUILD_DIR/lib/turboflow_adapter"

echo "  ✓ main.py"
echo "  ✓ requirements.txt"
echo "  ✓ lib/turboflow_adapter/"

# Count files
FILE_COUNT=$(find "$BUILD_DIR" -type f | wc -l)
echo ""
echo "Build complete: $FILE_COUNT files in $BUILD_DIR"
