#!/usr/bin/env python3
"""
Script to convert raw API calls to Postman folder format following the guidelines
in 'postman collection creation.md'
"""

import json
import re
import os
from typing import Dict, Any, List, Union

class PostmanFolderGenerator:
    def __init__(self):
        self.pre_request_script = [
            "function removePlaceholders(obj) {",
            "    const placeholderPattern = /{{.*}}/;",
            "    if (Array.isArray(obj)) {",
            "        for (let i = obj.length - 1; i >= 0; i--) {",
            "            if (obj[i] === null || obj[i] === \"\" || obj[i] === \"null\" || placeholderPattern.test(obj[i])) {",
            "                obj.splice(i, 1);",
            "            } else if (typeof obj[i] === 'object') {",
            "                removePlaceholders(obj[i]);",
            "                if (Object.keys(obj[i]).length === 0) {",
            "                    obj.splice(i, 1);",
            "                }",
            "            }",
            "        }",
            "    } else {",
            "        for (let key in obj) {",
            "            if (obj[key] === null || obj[key] === \"\" || obj[key] === \"null\" || placeholderPattern.test(obj[key])) {",
            "                delete obj[key];",
            "            } else if (typeof obj[key] === 'object') {",
            "                removePlaceholders(obj[key]);",
            "                if (Object.keys(obj[key]).length === 0) {",
            "                    delete obj[key];",
            "                }",
            "            }",
            "        }",
            "    }",
            "}",
            "",
            "let body = pm.request.body.raw;",
            "    // console.log(\"Original Payload:\", body);",
            "",
            "try {",
            "    // Replace placeholders with null to make the JSON valid",
            "    body = body.replace(/{{.*?}}/g, 'null');",
            "    // console.log(\"Payload with placeholders replaced:\", body);",
            "",
            "    body = JSON.parse(body);",
            "    console.log(\"Parsed Payload:\", body);",
            "",
            "    removePlaceholders(body);",
            "    pm.request.body.raw = JSON.stringify(body, null, 2);",
            "    console.log(\"Modified Payload:\", pm.request.body.raw);",
            "} catch (e) {",
            "    console.error(\"Error parsing JSON:\", e);",
            "}"
        ]

    def convert_values_to_variables(self, obj: Any, parent_key: str = None, path: List[str] = None) -> Any:
        """
        Convert values to Postman variables following the naming convention
        """
        if path is None:
            path = []
        
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                new_path = path + [key]
                result[key] = self.convert_values_to_variables(value, key, new_path)
            return result
        elif isinstance(obj, list):
            if len(obj) == 1 and isinstance(obj[0], (str, int, float, bool)):
                # Single item array, treat as single value
                var_name = self.generate_variable_name(parent_key, path)
                if isinstance(obj[0], str):
                    return [f"{{{{{var_name}}}}}"]
                else:
                    # For numbers and booleans, use special marker for no quotes
                    return [f"__NO_QUOTES__{{{{{var_name}}}}}__NO_QUOTES__"]
            else:
                # Multiple items or complex objects - don't add index to path
                return [self.convert_values_to_variables(item, parent_key, path) for item in obj]
        elif isinstance(obj, str):
            var_name = self.generate_variable_name(parent_key, path)
            return f"{{{{{var_name}}}}}"
        elif isinstance(obj, bool):
            var_name = self.generate_variable_name(parent_key, path)
            # Use special marker for boolean values (no quotes)
            return f"__NO_QUOTES__{{{{{var_name}}}}}__NO_QUOTES__"
        elif isinstance(obj, (int, float)):
            var_name = self.generate_variable_name(parent_key, path)
            # Use special marker for numeric values (no quotes)
            return f"__NO_QUOTES__{{{{{var_name}}}}}__NO_QUOTES__"
        else:
            return obj

    def generate_variable_name(self, key: str, path: List[str]) -> str:
        """
        Generate a variable name based on the key and path
        """
        if not key:
            return "variable"
        
        # Special handling for name and description fields
        if key == "name":
            return "profile_name"
        elif key == "description":
            return "profile_description"
        
        # Convert kebab-case to snake_case and clean up
        var_name = key.replace('-', '_')
        var_name = re.sub(r'[^a-zA-Z0-9_]', '_', var_name)
        var_name = re.sub(r'_+', '_', var_name)
        var_name = var_name.strip('_')
        
        # Add context from parent keys if needed for uniqueness
        if len(path) > 2:
            parent = path[-2].replace('-', '_')
            parent = re.sub(r'[^a-zA-Z0-9_]', '_', parent)
            if parent and parent != var_name and not var_name.startswith(parent):
                var_name = f"{parent}_{var_name}"
        
        return var_name

    def parse_api_call_file(self, file_path: str) -> tuple:
        """
        Parse the API call file and extract API name and payload
        """
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Extract API name
        api_name_match = re.search(r'api_name:\s*"([^"]*)"', content)
        if not api_name_match:
            raise ValueError("API name not found in the file")
        
        api_name = api_name_match.group(1).lower()
        
        # Find the start and end of the two JSON objects
        lines = content.split('\n')
        
        # Find the first JSON object (with api_name) - we'll skip this
        first_brace_count = 0
        first_obj_end = None
        
        for i, line in enumerate(lines):
            if '{' in line:
                first_brace_count += line.count('{')
            if '}' in line:
                first_brace_count -= line.count('}')
                if first_brace_count == 0:
                    first_obj_end = i
                    break
        
        if first_obj_end is None:
            raise ValueError("Could not find end of first JSON object")
        
        # The second JSON object starts after the comma
        json_start = first_obj_end + 1
        while json_start < len(lines) and lines[json_start].strip() in ['', ',']:
            json_start += 1
        
        if json_start >= len(lines):
            raise ValueError("Could not find second JSON object")
        
        json_content = '\n'.join(lines[json_start:])
        
        try:
            payload = json.loads(json_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in payload: {e}")
        
        return api_name, payload

    def create_postman_request(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Postman request following the guidelines
        """
        # Convert payload values to variables
        converted_payload = self.convert_values_to_variables(payload)
        
        # Create the raw body string
        raw_body = json.dumps(converted_payload, indent=4)
        
        # Remove quotes from numeric and boolean variables
        raw_body = re.sub(r'"__NO_QUOTES__(\{\{[^}]+\}\})__NO_QUOTES__"', r'\1', raw_body)
        
        # Determine request name
        request_name = f"Create {api_name.lower()} Profile" if "profile" in payload else f"Create {api_name.lower()}"
        
        # Create the request structure
        request = {
            "name": request_name,
            "event": [
                {
                    "listen": "prerequest",
                    "script": {
                        "exec": self.pre_request_script,
                        "type": "text/javascript"
                    }
                }
            ],
            "request": {
                "method": "POST",
                "header": [],
                "auth": {
                    "type": "bearer",
                    "bearer": [
                        {
                            "key": "token",
                            "value": "{{central_token}}",
                            "type": "string"
                        }
                    ]
                },
                "body": {
                    "mode": "raw",
                    "raw": raw_body,
                    "options": {
                        "raw": {
                            "language": "json"
                        }
                    }
                },
                "url": {
                    "raw": f"{{{{central_api_base_url}}}}/network-config/v1alpha1/{api_name}",
                    "host": [
                        "{{central_api_base_url}}"
                    ],
                    "path": [
                        "network-config",
                        "v1alpha1",
                        api_name
                    ],
                    "query": [
                        {
                            "key": "object_type",
                            "value": "LOCAL",
                            "disabled": True
                        },
                        {
                            "key": "scope_id",
                            "value": "{{scope_id}}",
                            "description": "ID of scope to create profile",
                            "disabled": True
                        },
                        {
                            "key": "persona",
                            "value": "{{persona}}",
                            "description": "Device function category to create profile under",
                            "disabled": True
                        }
                    ]
                }
            },
            "response": []
        }
        
        return request

    def create_postman_folder(self, api_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a complete Postman folder
        """
        request = self.create_postman_request(api_name, payload)
        
        folder = {
            "name": api_name.lower(),
            "item": [request],
            "description": "Matched Lines:"
        }
        
        return folder

    def add_folder_to_collection(self, folder: Dict[str, Any], collection_file: str) -> None:
        """
        Add the folder to an existing Postman collection
        """
        # Read existing collection
        with open(collection_file, 'r') as f:
            collection = json.load(f)
        
        # Add the new folder to the items
        collection["item"].append(folder)
        
        # Write back to file
        with open(collection_file, 'w') as f:
            json.dump(collection, f, indent=4)

def main():
    """
    Main function to convert API call to Postman folder
    """
    # File paths
    api_call_file = "api_call.txt"
    collection_file = "postman-database.json"
    
    # Check if files exist
    if not os.path.exists(api_call_file):
        print(f"Error: {api_call_file} not found")
        return
    
    if not os.path.exists(collection_file):
        print(f"Error: {collection_file} not found")
        return
    
    try:
        # Create generator instance
        generator = PostmanFolderGenerator()
        
        # Parse the API call file
        print(f"Parsing {api_call_file}...")
        api_name, payload = generator.parse_api_call_file(api_call_file)
        print(f"Found API: {api_name}")
        
        # Create Postman folder
        print("Creating Postman folder...")
        folder = generator.create_postman_folder(api_name, payload)
        
        # Add to collection
        print(f"Adding folder to {collection_file}...")
        generator.add_folder_to_collection(folder, collection_file)
        
        # Also save the folder as a separate file for review
        # folder_file = f"postman_folder_{api_name}.json"
        # with open(folder_file, 'w') as f:
        #     json.dump(folder, f, indent=4)
        
        print(f"✅ Successfully created Postman folder for {api_name}")
        print(f"📁 Folder added to {collection_file}")
        # print(f"📄 Standalone folder saved as {folder_file}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
