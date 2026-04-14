# Prompts

## Zero-Shot

You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

For each key data element, provide:
- name: the name of the key data element
- requirements: a list of requirements associated with that element

Document:
{text}

Identify all key data elements in the document above.

---

## Few-Shot

You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

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

Identify all key data elements in the document above following the same format as the examples.

---

## Chain-of-Thought

You are a security requirements analyst. Read the following security requirements document and identify the key data elements (KDEs).

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

Now let's work through this step by step to identify all key data elements in the document above.