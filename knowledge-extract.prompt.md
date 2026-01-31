curl -X POST http://ollama:11434/api/generate -d '{
  "model": "llama3",
  "stream": false,
  "format": {
    "type": "object",
    "properties": {
      "entities": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "relationships": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "source": { "type": "string" },
            "target": { "type": "string" },
            "relation": { 
              "type": "string"
            },
            "description": { "type": "string" }
          },
          "required": ["source", "target", "relation", "description"]
        }
      }
    },
    "required": ["entities", "relationships"]
  },
  "prompt": "Analyze the following documentation text and extract the knowledge graph. IMPORTANT: The \"relation\" field must be a single word in snake_case (e.g. \"matches_column\", \"has_type\").\n\n\n\nTEXT TO ANALYZE:\n\"\"\"\nThe field editor allows users to define fields for objects managed by Xperience (content types, system classes, object types). Each field matches a column in the database table belonging to the corresponding object. \n\nA field’s main attributes are its:\n\nname – a unique identifier.\ndata type – the type of data stored by the field in the underlying database column (string, integer, binary, etc.).\nassigned value editor – the input interface used to edit the field. Dictated by the UI form component selected to manage the field (a drop-down list, check box, etc.).\n\"\"\"\n\nReturn the JSON structure with two keys: \"entities\" (list of strings) and \"relationships\" (list of objects with source, target, relation, description)."
}'