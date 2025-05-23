#!/bin/bash
set -e

# Print environment variables for debugging (optional)
echo "--- Container Environment Variables ---"
echo "PYTHONPATH: $PYTHONPATH"
echo "MAX_STEPS: $MAX_STEPS"
echo "DEBUG: $DEBUG"
echo "ALLOWED_WRITE_DIR: $ALLOWED_WRITE_DIR"
echo "USER: $(whoami)"
echo "Current directory: $(pwd)"
echo "-------------------------------------"

# The WORKDIR in Dockerfile is /app, which is the project root.
# start.py and tools_patch.py are now directly in /app.
# nanoOpenManus (the package) is also in /app.
echo "Executing application..."
exec python /app/start.py "$@" 