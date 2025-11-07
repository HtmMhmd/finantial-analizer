#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from doc_analizer.crew import DocAnalizer

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'file_paths': ['/workspaces/doc_analizer/tests/sample_pdfs/Personal-Loan-Application-Form.pdf'],
        'analysis_type': 'personal_loan_application_review',
    }

    try:
        result = DocAnalizer().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
