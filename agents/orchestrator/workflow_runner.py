# orchestrator/workflow_runner.py
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from workflows.email_pipeline import email_pipeline

if __name__ == "__main__":
    email_pipeline(folder_name='test')
