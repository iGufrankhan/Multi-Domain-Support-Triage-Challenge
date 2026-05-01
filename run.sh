#!/bin/bash
# Quick start script for Linux/macOS

echo ""
echo "========================================"
echo "Multi-Domain Support Triage Agent"
echo "========================================"
echo ""

cd code

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

# Run the agent
echo "Starting agent..."
echo ""

python3 agent.py "$@"
