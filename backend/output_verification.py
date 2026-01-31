import requests
import json
import time

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"
MAX_RETRIES = 3

# The base text to analyze
TEXT_TO_ANALYZE = """
The field editor allows users to define fields for objects managed by Xperience (content types, system classes, object types). 
Each field matches a column in the database table belonging to the corresponding object. 
A field’s main attributes are its:
name – a unique identifier.
data type – the type of data stored by the field in the underlying database column.
assigned value editor – the input interface used to edit the field.
"""

# The Strict JSON Schema (Syntax)
JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "entities": {"type": "array", "items": {"type": "string"}},
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {"type": "string"},
                    "target": {"type": "string"},
                    "relation": {"type": "string", "pattern": "^[a-z0-9_]+$"}, # Enforce snake_case
                    "description": {"type": "string"}
                },
                "required": ["source", "target", "relation", "description"]
            }
        }
    },
    "required": ["entities", "relationships"]
}

def get_knowledge_graph(current_prompt, retry_count=0):
    payload = {
        "model": MODEL,
        "prompt": current_prompt,
        "format": JSON_SCHEMA,
        "stream": False
    }

    print(f"🔄 Attempt {retry_count + 1}...")
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return None

def validate_consistency(json_data):
    """
    Logic Check: Ensures all nodes in relationships exist in the entities list.
    """
    try:
        data = json.loads(json_data)
        
        # 1. Get explicit entities
        declared_entities = set(data.get("entities", []))
        
        # 2. Get entities referenced in relationships
        referenced_entities = set()
        for rel in data.get("relationships", []):
            referenced_entities.add(rel['source'])
            referenced_entities.add(rel['target'])
            
        # 3. Find missing ones
        missing = referenced_entities - declared_entities
        
        if missing:
            return False, list(missing), data
        return True, [], data

    except json.JSONDecodeError:
        return False, "JSON Decode Error", None

# --- Main Execution Loop ---
def main():
    # Initial Prompt
    base_prompt = f"""
    Analyze the text below and extract a knowledge graph.
    Rules:
    1. 'relation' must be snake_case (e.g. matches_column).
    2. Every object mentioned in 'relationships' MUST also be listed in the 'entities' array.
    
    TEXT: {TEXT_TO_ANALYZE}
    """
    
    current_prompt = base_prompt

    for i in range(MAX_RETRIES):
        response_text = get_knowledge_graph(current_prompt, i)
        
        if not response_text:
            break

        is_valid, missing_or_error, parsed_data = validate_consistency(response_text)

        if is_valid:
            print("\n✅ Success! Valid & Consistent Graph Extracted:")
            print(json.dumps(parsed_data, indent=2))
            return parsed_data
        else:
            print(f"⚠️ Consistency Check Failed: Missing entities {missing_or_error}")
            
            # THE KEY: Refine the prompt with specific feedback for the model
            current_prompt = (
                f"{base_prompt}\n\n"
                f"PREVIOUS ERROR: You generated a valid JSON structure, but you forgot to list these items "
                f"in the 'entities' array: {missing_or_error}. \n"
                f"Please regenerate the JSON and ensure {missing_or_error} are included in the 'entities' list."
            )
            time.sleep(1) # Be nice to the API

    print("\n❌ Failed to get a consistent result after max retries.")

if __name__ == "__main__":
    main()