import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from tasks.comparator import (
    load_yaml_files,
    compare_element_names,
    compare_element_requirements
)

# Create sample YAML files for testing
def create_sample_yamls():
    import yaml

    yaml1 = {
        "element1": {
            "name": "API Server Authentication",
            "requirements": {
                "req1": "Ensure strong authentication",
                "req2": "Disable anonymous authentication"
            }
        },
        "element2": {
            "name": "Network Policies",
            "requirements": {
                "req1": "Restrict traffic between namespaces"
            }
        }
    }

    yaml2 = {
        "element1": {
            "name": "API Server Authentication",
            "requirements": {
                "req1": "Ensure strong authentication"
            }
        },
        "element2": {
            "name": "Logging",
            "requirements": {
                "req1": "Enable audit logging"
            }
        }
    }

    with open("outputs/test_yaml1.yaml", "w") as f:
        yaml.dump(yaml1, f)
    with open("outputs/test_yaml2.yaml", "w") as f:
        yaml.dump(yaml2, f)

# Test 1: load_yaml_files
def test_load_yaml_files():
    create_sample_yamls()
    yaml1, yaml2 = load_yaml_files("outputs/test_yaml1.yaml", "outputs/test_yaml2.yaml")
    assert isinstance(yaml1, dict)
    assert isinstance(yaml2, dict)

# Test 2: compare_element_names
def test_compare_element_names():
    create_sample_yamls()
    yaml1, yaml2 = load_yaml_files("outputs/test_yaml1.yaml", "outputs/test_yaml2.yaml")
    differences = compare_element_names(yaml1, yaml2, "test_name_differences.txt")
    assert isinstance(differences, set)
    assert "Logging" in differences
    assert "Network Policies" in differences

# Test 3: compare_element_requirements
def test_compare_element_requirements():
    create_sample_yamls()
    yaml1, yaml2 = load_yaml_files("outputs/test_yaml1.yaml", "outputs/test_yaml2.yaml")
    differences = compare_element_requirements(yaml1, yaml2, "test_req_differences.txt")
    assert isinstance(differences, set)
    assert len(differences) > 0