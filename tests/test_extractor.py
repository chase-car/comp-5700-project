import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from tasks.extractor import (
    load_document,
    construct_zero_shot_prompt,
    construct_few_shot_prompt,
    construct_chain_of_thought_prompt,
    extract_kdes,
    save_llm_output
)

# Test 1: load_document
def test_load_document():
    text = load_document("pdfs/cis-r1.pdf")
    assert isinstance(text, str)
    assert len(text) > 0

# Test 2: construct_zero_shot_prompt
def test_construct_zero_shot_prompt():
    prompt = construct_zero_shot_prompt("sample text")
    assert isinstance(prompt, str)
    assert "sample text" in prompt

# Test 3: construct_few_shot_prompt
def test_construct_few_shot_prompt():
    prompt = construct_few_shot_prompt("sample text")
    assert isinstance(prompt, str)
    assert "sample text" in prompt

# Test 4: construct_chain_of_thought_prompt
def test_construct_chain_of_thought_prompt():
    prompt = construct_chain_of_thought_prompt("sample text")
    assert isinstance(prompt, str)
    assert "sample text" in prompt

# Test 5: extract_kdes
def test_extract_kdes():
    text = load_document("pdfs/cis-r1.pdf")
    prompt = construct_zero_shot_prompt(text)
    kdes = extract_kdes(text, prompt, "zero-shot", "cis-r1")
    assert isinstance(kdes, dict)

# Test 6: save_llm_output
def test_save_llm_output():
    save_llm_output("gemma-3-1b-it", "test prompt", "zero-shot", "test output", "test_output.txt")
    assert os.path.exists("outputs/test_output.txt")