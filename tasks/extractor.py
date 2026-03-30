import fitz
import os
import yaml
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

def load_document(filepath):
    """
    Takes a PDF filepath as input, validates it, and returns the full text.
    """
    # Check if file exists
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    
    # Check if file is a PDF
    if not filepath.endswith(".pdf"):
        raise ValueError(f"File is not a PDF: {filepath}")
    
    # Open and extract text
    doc = fitz.open(filepath)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()

    if not full_text.strip():
        raise ValueError(f"No text could be extracted from: {filepath}")

    return full_text

def construct_zero_shot_prompt(text):
    """
    Constructs a zero shot prompt to identify key data elements in a document.
    Returns a string.
    """
    prompt = f"""You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

For each key data element, provide:
- name: the name of the key data element
- requirements: a list of requirements associated with that element

Document:
{text}

Identify all key data elements in the document above."""

    return prompt

def construct_few_shot_prompt(text):
    """
    Constructs a few shot prompt to identify key data elements in a document.
    Returns a string.
    """
    prompt = f"""You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

For each key data element, provide:
- name: the name of the key data element
- requirements: a list of requirements associated with that element

Here are some examples of key data elements and their requirements:

Example 1:
name: API Server Authentication
requirements:
  - req1: Ensure that the API server is configured to use strong authentication
  - req2: Ensure that anonymous authentication is disabled
  - req3: Ensure that client certificate authentication is enabled

Example 2:
name: Network Policies
requirements:
  - req1: Ensure that network policies are configured to restrict traffic
  - req2: Ensure that all namespaces have network policies defined
  - req3: Ensure that default deny policies are in place

Now identify all key data elements in the following document:

Document:
{text}

Identify all key data elements in the document above following the same format as the examples."""

    return prompt

def construct_chain_of_thought_prompt(text):
    """
    Constructs a chain of thought prompt to identify key data elements in a document.
    Returns a string.
    """
    prompt = f"""You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

Let's think through this step by step:

Step 1: Read through the document carefully and identify the main topics and sections.
Step 2: For each section, identify the key data elements that are being discussed.
Step 3: For each key data element, identify the specific requirements associated with it.
Step 4: Organize the key data elements and their requirements in a structured format.

For each key data element, provide:
- name: the name of the key data element
- requirements: a list of requirements associated with that element

Document:
{text}

Now let's work through this step by step to identify all key data elements in the document above."""

    return prompt

def extract_kdes(text, prompt, prompt_type, doc_name):
    """
    Uses Gemma-3-1B to extract key data elements from a document.
    Saves the output to a YAML file and returns a nested dictionary.
    """
    model_name = "google/gemma-3-1b-it"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32)

    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=2048)
    outputs = model.generate(**inputs, max_new_tokens=1024)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Build nested dictionary from response
    kdes = {}
    lines = response.split("\n")
    current_element = None
    element_count = 0

    for line in lines:
        line = line.strip()
        if line.lower().startswith("name:"):
            element_count += 1
            current_element = f"element{element_count}"
            kdes[current_element] = {
                "name": line.replace("name:", "").strip(),
                "requirements": {}
            }
        elif line.lower().startswith("- req") and current_element:
            req_key = f"req{len(kdes[current_element]['requirements']) + 1}"
            kdes[current_element]["requirements"][req_key] = line.lstrip("- ").strip()

    # Save to YAML file
    yaml_filename = f"outputs/{doc_name}-kdes.yaml"
    with open(yaml_filename, "w") as f:
        yaml.dump(kdes, f, default_flow_style=False)

    return kdes

def save_llm_output(llm_name, prompt, prompt_type, llm_output, output_filename):
    """
    Collects LLM output and saves it to a TEXT file in a formatted way.
    """
    with open(f"outputs/{output_filename}", "a") as f:
        f.write(f"*LLM Name*\n")
        f.write(f"{llm_name}\n\n")
        f.write(f"*Prompt Used*\n")
        f.write(f"{prompt}\n\n")
        f.write(f"*Prompt Type*\n")
        f.write(f"{prompt_type}\n\n")
        f.write(f"*LLM Output*\n")
        f.write(f"{llm_output}\n\n")
        f.write("="*50 + "\n\n")