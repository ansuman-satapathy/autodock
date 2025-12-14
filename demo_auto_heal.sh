#!/bin/bash

set -e

echo "🚀 AutoDock Auto-Healing Demo"
echo "=============================="

if ! command -v cline &> /dev/null; then
    echo "❌ Error: 'cline' CLI not found. Install it with: npm install -g cline"
    exit 1
fi

echo "✅ Cline CLI found"
echo "🔧 Starting auto-healing workflow for container 'test-fixer'..."

cline task new -y "The docker container 'test-fixer' is down.
CRITICAL INSTRUCTION: You must use the 'autodock' MCP tools to handle this.
1. Call tool 'diagnose_container' (argument: 'container_id') to get the status.
2. Call tool 'analyze_logs' (argument: 'container_id') to check for errors.
3. Call tool 'fix_container' (argument: 'container_id') to restart it.
DO NOT use raw 'docker' terminal commands."

echo "✅ Task dispatched."
echo "👀 To watch progress, run: cline task view --follow"