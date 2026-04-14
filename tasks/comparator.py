import yaml
import os

def load_yaml_files(filepath1, filepath2):

    # Check if files exist
    if not os.path.exists(filepath1):
        raise FileNotFoundError(f"File not found: {filepath1}")
    if not os.path.exists(filepath2):
        raise FileNotFoundError(f"File not found: {filepath2}")

    # Check if files are YAML
    if not filepath1.endswith(".yaml"):
        raise ValueError(f"File is not a YAML file: {filepath1}")
    if not filepath2.endswith(".yaml"):
        raise ValueError(f"File is not a YAML file: {filepath2}")

    # Load the YAML files
    with open(filepath1, "r") as f:
        yaml1 = yaml.safe_load(f)
    with open(filepath2, "r") as f:
        yaml2 = yaml.safe_load(f)

    return yaml1, yaml2

def compare_element_names(yaml1, yaml2, output_filename):
    """
    Identifies differences in element names between two YAML files.
    Saves the differences to a TEXT file.
    """
    names1 = set()
    names2 = set()

    if yaml1:
        for element in yaml1.values():
            if element and "name" in element:
                names1.add(element["name"])

    if yaml2:
        for element in yaml2.values():
            if element and "name" in element:
                names2.add(element["name"])

    differences = names1.symmetric_difference(names2)

    with open(f"outputs/{output_filename}", "w") as f:
        if differences:
            for name in differences:
                f.write(f"{name}\n")
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT NAMES\n")

    return differences

def compare_element_requirements(yaml1, yaml2, output_filename):
    """
    Identifies differences in element requirements between two YAML files.
    Saves the differences to a TEXT file as tuples (NAME, REQUIREMENT).
    """
    reqs1 = set()
    reqs2 = set()

    if yaml1:
        for element in yaml1.values():
            if element and "name" in element and "requirements" in element:
                name = element["name"]
                if element["requirements"]:
                    for req in element["requirements"].values():
                        reqs1.add((name, req))

    if yaml2:
        for element in yaml2.values():
            if element and "name" in element and "requirements" in element:
                name = element["name"]
                if element["requirements"]:
                    for req in element["requirements"].values():
                        reqs2.add((name, req))

    differences = reqs1.symmetric_difference(reqs2)

    with open(f"outputs/{output_filename}", "w") as f:
        if differences:
            for name, req in differences:
                f.write(f"{name},{req}\n")
        else:
            f.write("NO DIFFERENCES IN REGARDS TO ELEMENT REQUIREMENTS\n")

    return differences