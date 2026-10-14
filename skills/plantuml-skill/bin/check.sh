#!/usr/bin/env bash
set -euo pipefail

echo "=== PlantUML Offline Renderer Check ==="
JAR="$HOME/.config/opencode/skills/plantuml-skill/bin/plantuml.jar"

if [ -f "$JAR" ]; then
  echo "✅ plantuml.jar: found at $JAR ($(du -h "$JAR" | cut -f1))"
else
  echo "❌ plantuml.jar not found. Download it first."
fi

if command -v java &>/dev/null; then
  echo "✅ Java: $(java -version 2>&1 | head -1)"
else
  echo "❌ Java not installed"
fi

if command -v dot &>/dev/null; then
  echo "✅ Graphviz: $(dot -V 2>&1 | head -1)"
else
  echo "⚠️  Graphviz not installed (needed for activity/class diagrams)"
fi

if curl --version &>/dev/null; then
  echo "✅ curl: available"
else
  echo "❌ curl not installed"
fi
