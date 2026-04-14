import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tasks.extractor import (
    load_document,
    construct_zero_shot_prompt,
    construct_few_shot_prompt,
    construct_chain_of_thought_prompt,
    extract_kdes,
    save_llm_output
)

# Nine input combinations
inputs = [
    ("pdfs/cis-r1.pdf", "pdfs/cis-r1.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r2.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r1.pdf", "pdfs/cis-r4.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r2.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r2.pdf", "pdfs/cis-r4.pdf"),
    ("pdfs/cis-r3.pdf", "pdfs/cis-r3.pdf"),
    ("pdfs/cis-r3.pdf", "pdfs/cis-r4.pdf"),
]

prompt_types = [
    ("zero-shot", construct_zero_shot_prompt),
    ("few-shot", construct_few_shot_prompt),
    ("chain-of-thought", construct_chain_of_thought_prompt),
]

llm_name = "google/gemma-3-1b-it"

for doc1_path, doc2_path in inputs:
    # Get document names without extension
    doc1_name = os.path.basename(doc1_path).replace(".pdf", "")
    doc2_name = os.path.basename(doc2_path).replace(".pdf", "")

    print(f"\nProcessing: {doc1_name} and {doc2_name}")

    # Load documents
    text1 = load_document(doc1_path)
    text2 = load_document(doc2_path)

    for prompt_type, construct_prompt in prompt_types:
        print(f"  Using prompt type: {prompt_type}")

        # Construct prompts
        prompt1 = construct_prompt(text1)
        prompt2 = construct_prompt(text2)

        # Extract KDEs
        kdes1 = extract_kdes(text1, prompt1, prompt_type, f"{doc1_name}-{prompt_type}")
        kdes2 = extract_kdes(text2, prompt2, prompt_type, f"{doc2_name}-{prompt_type}")

        # Save LLM outputs
        output_filename = f"{doc1_name}-{doc2_name}-{prompt_type}-llm-output.txt"
        save_llm_output(llm_name, prompt1, prompt_type, str(kdes1), output_filename)
        save_llm_output(llm_name, prompt2, prompt_type, str(kdes2), output_filename)

print("\nPipeline complete! Check the outputs/ folder for results.")