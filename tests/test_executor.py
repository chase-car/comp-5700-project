import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
from tasks.executor import (
    load_text_files,
    determine_controls,
    execute_kubescape,
    generate_csv
)

# Create sample TEXT files for testing
def create_sample_text_files():
    with open("outputs/test_names.txt", "w") as f:
        f.write("Network Policies\nLogging\nAuthentication\n")

    with open("outputs/test_reqs.txt", "w") as f:
        f.write("Network Policies,Ensure network policies are configured\n")
        f.write("Logging,Ensure audit logging is enabled\n")

def create_no_diff_text_files():
    with open("outputs/test_no_diff_names.txt", "w") as f:
        f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES\n")

    with open("outputs/test_no_diff_reqs.txt", "w") as f:
        f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS\n")

# Test 1: load_text_files
def test_load_text_files():
    create_sample_text_files()
    text1, text2 = load_text_files("outputs/test_names.txt", "outputs/test_reqs.txt")
    assert isinstance(text1, str)
    assert isinstance(text2, str)
    assert len(text1) > 0
    assert len(text2) > 0

# Test 2: determine_controls
def test_determine_controls():
    create_sample_text_files()
    text1, text2 = load_text_files("outputs/test_names.txt", "outputs/test_reqs.txt")
    controls = determine_controls(text1, text2, "test_controls.txt")
    assert isinstance(controls, set)
    assert len(controls) > 0

# Test 3: execute_kubescape
def test_execute_kubescape():
    create_sample_text_files()
    determine_controls(
        "outputs/test_names.txt",
        "outputs/test_reqs.txt",
        "test_controls.txt"  
    )
    # We test that the function returns a dataframe even if kubescape is not installed
    df = execute_kubescape("outputs/test_controls.txt", "project-yamls.zip")
    assert isinstance(df, pd.DataFrame)

# Test 4: generate_csv
def test_generate_csv():
    # Create a sample dataframe
    df = pd.DataFrame([{
        "FilePath": "test/path.yaml",
        "Severity": "High",
        "Control name": "Test Control",
        "Failed resources": 1,
        "All Resources": 5,
        "Compliance score": 80
    }])
    csv_path = generate_csv(df, "test_results.csv")
    assert os.path.exists(csv_path)
    loaded_df = pd.read_csv(csv_path)
    assert list(loaded_df.columns) == ["FilePath", "Severity", "Control name",
                                        "Failed resources", "All Resources", "Compliance score"]