
import os
import sys

# Ensure we can import from local modules
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "backend-services"))

from job_search_engine import run_automated_search

if __name__ == "__main__":
    run_automated_search()
