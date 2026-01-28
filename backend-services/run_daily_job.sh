#!/bin/bash
# Wrapper script for Job Search Automation
# Required for Cron to ensure correct path and environment

# Set Project Directory
PROJECT_DIR="/Users/ivan/Desktop/Escritorio - Mini/Buscar_trabajo/Cloud-AI-Job-Engine"
LOG_FILE="$PROJECT_DIR/job_search.log"

# Go to directory
cd "$PROJECT_DIR" || exit 1

# Export any necessary Path variables if needed, though full path to python handles most.
# Define Python Path
PYTHON_EXEC="/Library/Frameworks/Python.framework/Versions/3.13/bin/python3"

# Run Script
echo "------------------------------------------------" >> "$LOG_FILE"
echo "Starting Job Search at $(date)" >> "$LOG_FILE"

"$PYTHON_EXEC" "backend-services/automate_search.py" >> "$LOG_FILE" 2>&1

echo "Finished Job Search at $(date)" >> "$LOG_FILE"
echo "------------------------------------------------" >> "$LOG_FILE"
