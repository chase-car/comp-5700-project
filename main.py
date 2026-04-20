import sys
import os
from tasks.extractor import (
    load_document,
    construct_zero_shot_prompt,
    construct_few_shot_prompt,
    construct_chain_of_thought_prompt,
    extract_kdes,
    save_llm_output
)
from tasks.comparator import (
    load_yaml_files,
    compare_element_names,
    compare_element_requirements
)
from tasks.executor import (
    load_text_files,
    determine_controls,
    execute_kubescape,
    generate_csv
)

if __name__ == "__main__":
    print("Starting pipeline...")
    print(f"Arguments: {sys.argv}")
    if len(sys.argv) != 3:
        print("Usage: python main.py <doc1.pdf> <doc2.pdf>")
        sys.exit(1)

def run_pipeline(doc1_path, doc2_path):
    """
    Runs the full pipeline on two PDF documents.
    """
    # Get document names without extension
    doc1_name = os.path.basename(doc1_path).replace(".pdf", "")
    doc2_name = os.path.basename(doc2_path).replace(".pdf", "")

    print(f"\nProcessing: {doc1_name} and {doc2_name}")

    # Task 1: Extract KDEs
    print("Running Task 1: Extracting KDEs...")
    text1 = load_document(doc1_path)
    text2 = load_document(doc2_path)

    prompt_types = [
        ("zero-shot", construct_zero_shot_prompt),
        ("few-shot", construct_few_shot_prompt),
        ("chain-of-thought", construct_chain_of_thought_prompt),
    ]

    llm_name = "google/gemma-3-1b-it"
    yaml1_path = None
    yaml2_path = None

    for prompt_type, construct_prompt in prompt_types:
        print(f"  Using prompt type: {prompt_type}")
        prompt1 = construct_prompt(text1)
        prompt2 = construct_prompt(text2)

        kdes1 = extract_kdes(text1, prompt1, prompt_type, f"{doc1_name}-{prompt_type}")
        kdes2 = extract_kdes(text2, prompt2, prompt_type, f"{doc2_name}-{prompt_type}")

        output_filename = f"{doc1_name}-{doc2_name}-{prompt_type}-llm-output.txt"
        save_llm_output(llm_name, prompt1, prompt_type, str(kdes1), output_filename)
        save_llm_output(llm_name, prompt2, prompt_type, str(kdes2), output_filename)

        # Use zero-shot YAML files for comparison
        if prompt_type == "zero-shot":
            yaml1_path = f"outputs/{doc1_name}-zero-shot-kdes.yaml"
            yaml2_path = f"outputs/{doc2_name}-zero-shot-kdes.yaml"

    # Task 2: Compare KDEs
    print("Running Task 2: Comparing KDEs...")
    yaml1, yaml2 = load_yaml_files(yaml1_path, yaml2_path)

    names_output = f"{doc1_name}-{doc2_name}-name-differences.txt"
    reqs_output = f"{doc1_name}-{doc2_name}-req-differences.txt"

    compare_element_names(yaml1, yaml2, names_output)
    compare_element_requirements(yaml1, yaml2, reqs_output)

    # Task 3: Execute Kubescape
    print("Running Task 3: Executing Kubescape...")
    text1, text2 = load_text_files(
        f"outputs/{names_output}",
        f"outputs/{reqs_output}"
    )

    controls_output = f"{doc1_name}-{doc2_name}-controls.txt"
    determine_controls(text1, text2, controls_output)

    df = execute_kubescape(
        f"outputs/{controls_output}",
        "project-yamls.zip"
    )

    csv_output = f"{doc1_name}-{doc2_name}-results.csv"
    generate_csv(df, csv_output)

    print(f"\nPipeline complete! Check the outputs/ folder for results.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <doc1.pdf> <doc2.pdf>")
        sys.exit(1)

    doc1_path = sys.argv[1]
    doc2_path = sys.argv[2]

    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)

    run_pipeline(doc1_path, doc2_path)