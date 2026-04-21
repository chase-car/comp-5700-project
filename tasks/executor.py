import os
import pandas as pd
import subprocess

def load_text_files(filepath1, filepath2):
    """
    Takes two text file paths as input, validates them, and returns their contents
    """
    # Check if files exist
    if not os.path.exists(filepath1):
        raise FileNotFoundError(f"File not found: {filepath1}")
    if not os.path.exists(filepath2):
        raise FileNotFoundError(f"File not found: {filepath2}")

    # Check if files are text files
    if not filepath1.endswith(".txt"):
        raise ValueError(f"File is not a TEXT file: {filepath1}")
    if not filepath2.endswith(".txt"):
        raise ValueError(f"File is not a TEXT file: {filepath2}")

    # Load the text files
    with open(filepath1, "r") as f:
        text1 = f.read()
    with open(filepath2, "r") as f:
        text2 = f.read()

    return text1, text2

def determine_controls(text1, text2, output_filename):
    """
    Determines if there are differences in the TEXT files and maps them to Kubescape controls,
    saves the output to a text file.
    """
    # Check if there are any differences
    no_diff_messages = [
        "NO DIFFERENCES IN REGARDS TO ELEMENT NAMES",
        "NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS"
    ]

    has_differences = True
    if any(msg in text1 for msg in no_diff_messages) and \
       any(msg in text2 for msg in no_diff_messages):
        has_differences = False

    # Kubescape controls mapping
    kubescape_controls = {
        "authentication": ["C-0013", "C-0015", "C-0017"],
        "authorization": ["C-0016", "C-0035"],
        "network": ["C-0030", "C-0041", "C-0044"],
        "logging": ["C-0026"],
        "secrets": ["C-0012", "C-0034"],
        "rbac": ["C-0035", "C-0036", "C-0037"],
        "pod": ["C-0016", "C-0038", "C-0046"],
        "container": ["C-0002", "C-0013", "C-0017"],
        "kubelet": ["C-0041", "C-0044"],
        "namespace": ["C-0052"],
        "image": ["C-0001"],
        "access": ["C-0035", "C-0034"],
        "privilege": ["C-0016", "C-0046"],
        "encryption": ["C-0012"],
        "audit": ["C-0026"],
    }

    controls = set()

    if has_differences:
        # Combine both texts for keyword matching
        combined_text = (text1 + " " + text2).lower()
        for keyword, control_list in kubescape_controls.items():
            if keyword in combined_text:
                controls.update(control_list)

    with open(f"outputs/{output_filename}", "w") as f:
        if not has_differences or not controls:
            f.write("NO DIFFERENCES FOUND\n")
        else:
            for control in sorted(controls):
                f.write(f"{control}\n")

    return controls

def execute_kubescape(controls_filepath, yamls_zip):
    """
    Executes Kubescape tool based on the controls in the text file,
    returns a pandas dataframe with the results
    """
    # Read the controls file
    with open(controls_filepath, "r") as f:
        content = f.read().strip()

    # Extract zip if needed
    import zipfile
    if zipfile.is_zipfile(yamls_zip):
        with zipfile.ZipFile(yamls_zip, 'r') as zip_ref:
            zip_ref.extractall("outputs/project-yamls")

    yamls_dir = "outputs/project-yamls"

    # Build kubescape command
    if content == "NO DIFFERENCES FOUND":
        # Run with all controls
        cmd = f"kubescape scan {yamls_dir} --format json --output outputs/kubescape-results.json"
    else:
        # Run with specific controls
        controls = [line.strip() for line in content.split("\n") if line.strip()]
        controls_str = ",".join(controls)
        cmd = f"kubescape scan control {controls_str} {yamls_dir} --format json --output outputs/kubescape-results.json"

    # Execute kubescape
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(f"Kubescape output: {result.stdout}")
    print(f"Kubescape errors: {result.stderr}")

    # Parse results
    import json
    try:
        with open("outputs/kubescape-results.json", "r") as f:
            results = json.load(f)

        rows = []
        for result in results.get("results", []):
            resource_id = result.get("resourceID", "")
            for control in result.get("controls", []):
                status = control.get("status", {}).get("status", "")
                if status == "failed":
                    rows.append({
                        "FilePath": resource_id,
                        "Severity": control.get("severity", ""),
                        "Control name": control.get("name", ""),
                        "Failed resources": 1,
                        "All Resources": 1,
                        "Compliance score": 0
                    })

        df = pd.DataFrame(rows).drop_duplicates() if rows else pd.DataFrame(
            columns=["FilePath", "Severity", "Control name",
                     "Failed resources", "All Resources", "Compliance score"])

    except Exception as e:
        print(f"Error parsing results: {e}")
        df = pd.DataFrame(columns=["FilePath", "Severity", "Control name",
                                    "Failed resources", "All Resources", "Compliance score"])

    return df

def generate_csv(df, output_filename):
    """
    Generates a CSV file from the kubescape scan results dataframe.
    """
    # Make sure the dataframe has the correct columns
    required_columns = ["FilePath", "Severity", "Control name", 
                        "Failed resources", "All Resources", "Compliance score"]
    
    # Add missing columns with empty values
    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    # Keep only required columns
    df = df[required_columns]

    # Save to CSV
    csv_path = f"outputs/{output_filename}"
    df.to_csv(csv_path, index=False)

    print(f"CSV saved to {csv_path}")

    return csv_path