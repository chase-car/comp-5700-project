# COMP 5700 Project

## Team Members
- Chase Carithers - cac0257@auburn.edu

## Project Description
This project automatically detects changes in two security requirements documents and executes a static analysis tool accordingly.

## LLM Used
- Model: google/gemma-3-1b-it
- Library: HuggingFace Transformers

## Project Structure
- `tasks/` - Source code for all tasks
  - `extractor.py` - Task 1: Extracts key data elements from PDF documents
  - `comparator.py` - Task 2: Compares key data elements across documents
  - `executor.py` - Task 3: Executes Kubescape based on differences
  - `run_pipeline.py` - Runs the full pipeline on all input combinations
- `tests/` - Test cases for all tasks
- `outputs/` - Generated YAML, TEXT, and CSV files
- `pdfs/` - Input PDF documents
- `PROMPT.md` - Prompts used for LLM

## Installation
```bash
python3 -m venv comp5700-venv
source comp5700-venv/Scripts/activate
pip install -r requirements.txt
```

## Usage
```bash
python3 tasks/run_pipeline.py
```