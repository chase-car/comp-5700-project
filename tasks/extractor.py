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
    model = AutoModelForCausalLM.from_pretrained(model_name, dtype=torch.float32)

    # Extract only relevant chunks from the document
    relevant_lines = []
    lines = text.split("\n")
    for i, line in enumerate(lines):
        line = line.strip()
        if any(line.startswith(kw) for kw in ["Ensure", "Minimize", "Avoid", "Prefer"]):
            # Grab the line and a few lines around it for context
            start = max(0, i-1)
            end = min(len(lines), i+4)
            chunk = "\n".join(lines[start:end])
            relevant_lines.append(chunk)

    # Build KDEs from chunks
    kdes = {}
    seen_names = set()
    element_count = 0
    for i, chunk in enumerate(relevant_lines):
        if element_count >= 5:
            break
        element_key = f"element{i+1}"

        short_prompt = f"""Extract the security requirement from this text and list any sub-requirements.
Format your response exactly like this:
name: <name of requirement>
- req1: <first requirement>
- req2: <second requirement>

Text:
{chunk}

Response:
name:"""

        inputs = tokenizer(short_prompt, return_tensors="pt", truncation=True, max_length=512)
        outputs = model.generate(**inputs, max_new_tokens=256)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Parse name - use the chunk's first meaningful line
        name = ""
        for chunk_line in chunk.split("\n"):
            chunk_line = chunk_line.strip()
            if any(chunk_line.startswith(kw) for kw in ["Ensure", "Minimize", "Avoid", "Prefer"]):
                name = chunk_line.split("(")[0].strip()
                break
        
        if not name or name in seen_names:
            continue  # Skip elements with no valid name or duplicates
        seen_names.add(name)
        element_count += 1

        # Parse requirements
        requirements = {}
        req_count = 1
        seen_reqs = set()

        for line in response.split("\n"):
            line = line.strip()
            # Skip placeholders and empty lines
            if not line or "<" in line:
                continue
            # Remove req1:, req2: prefixes if present
            if line.startswith("-"):
                req_val = line.lstrip("- ").strip()
                # Remove any reqN: prefix inside the value
                if req_val.startswith("req") and ":" in req_val:
                    req_val = req_val.split(":", 1)[1].strip()
                if req_val and req_val not in seen_reqs:
                    seen_reqs.add(req_val)
                    requirements[f"req{req_count}"] = req_val
                    req_count += 1

        kdes[f"element{element_count}"] = {
            "name": name,
            "requirements": requirements
        }

    # Save to YAML file
    yaml_filename = f"outputs/{doc_name}-kdes.yaml"
    with open(yaml_filename, "w") as f:
        yaml.dump(kdes, f, default_flow_style=False)

    return kdes

def save_llm_output(llm_name, prompt, prompt_type, llm_output, output_filename):
    """
    Collects LLM output and saves it to a TEXT file in a formatted way.
    """
    with open(f"outputs/{output_filename}", "a", encoding="utf-8") as f:
        f.write(f"*LLM Name*\n")
        f.write(f"{llm_name}\n\n")
        f.write(f"*Prompt Used*\n")
        f.write(f"{prompt}\n\n")
        f.write(f"*Prompt Type*\n")
        f.write(f"{prompt_type}\n\n")
        f.write(f"*LLM Output*\n")
        f.write(f"{llm_output}\n\n")
        f.write("="*50 + "\n\n")