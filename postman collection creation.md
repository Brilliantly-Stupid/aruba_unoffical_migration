# Manually Creating a Postman Folder JSON

This guide explains how to manually structure a Postman Folder JSON file from a raw API call. This guide uses NTP as an example.
The following rules should be followed:


- **The Pre-request Script is Mandatory** – It removes null values, empty strings, and placeholders (`{{variable}}`).
- **API Keys Remain Unchanged** – The keys in the raw API call should be preserved exactly as they are.
- **Values Become Variables** – The values should be replaced with `{{variable}}` notation to allow customization.
- **In the URL dictionary Path Ends with the API Name** – The last segment of the path should match the API name.
- **The Raw URL Ends with the API Name** – The raw URL should end with the API name.



## Raw API Call 

We will convert the following raw API call into a structured Postman Folder.
The API name is "ntp". The API name value will be used in multiple places. The key will not. 
### Raw API Call

```json
{
  api_name: "ntp" 
},
{
  "profile": [
    {
      "authenticate": false,
      "authentication-profile": [
        {
          "key-identifier": 4294967295,
          "key-hash": "MD5",
          "key-value": "string",
          "key-trusted": false,
          "ciphertext": {
            "key-value": "stringstringstring"
          }
        }
      ],
      "trusted-key": [65534],
      "conductor": [
        {
          "vrf": "string",
          "stratum": 15
        }
      ],
      "debug": false,
      "dhcp-disable": false,
      "source-interface": "VLAN",
      "source-vlan": 4094,
      "time-serve": [4094],
      "traps": ["NTP_MODE_CHANGE"],
      "servers": [
        {
          "address": "string",
          "tx-mode": "BURST",
          "burst": "SINGLE",
          "iburst": "ALWAYS",
          "key-identifier": 4294967295,
          "max-poll": 10,
          "min-poll": 6,
          "mgmt-interface": false,
          "prefer": false,
          "version": 4
        }
      ],
      "max-association": 8,
      "operation-mode": "BROADCAST",
      "server-mode-disable": false,
      "name": "string",
      "description": "string",
      "vrf": "string"
    }
  ]
}
```


## 1. Creating the Basic Structure of a Postman Folder

Every Postman Folder follows this JSON structure:

```json
{
            "name": "ntp",
            "item": [],
    "description": "Matched Lines:"
  
}
```

- **`name`**: The Folder name should be the API name.
- **`schema`**: Defines the format for Postman to recognize.

## 2.  Postman Request
The call below will be added to the item list in the basic structure of the Postman folder. Below are the steps to convert the raw API call into a Postman request.
The corresponding Postman request should keep the **keys** exactly the same as the raw API call but replace the **values** with variables wrapped in `{{variable}}`:
The name of the request should be "Create API Name" or "Create API Name Profile" use discretion .
The options field is a requirement and should always be added to the body field. This should always be added as is,
it allows the raw field to be formatted as JSON. 

The URL structure in Postman must adhere to the following:
The raw field must end with the API name.
The path field must include the API name as the last value.

```json
{
    "name": "Create NTP Profile",
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
            "raw": "{\n    \"profile\": [\n        {\n            \"authenticate\": {{authenticate}},\n            \"authentication-profile\": [\n                {\n                    \"key-identifier\": {{key_identifier}},\n                    \"key-hash\": \"{{key_hash}}\",\n                    \"key-value\": \"{{key_value}}\",\n                    \"key-trusted\": {{key_trusted}},\n                    \"ciphertext\": {\n                        \"key-value\": \"{{ciphertext_key_value}}\"\n                    }\n                }\n            ],\n            \"trusted-key\": [{{trusted_key}}],\n            \"conductor\": [\n                {\n                    \"vrf\": \"{{vrf}}\",\n                    \"stratum\": {{stratum}}\n                }\n            ],\n            \"debug\": {{debug}},\n            \"dhcp-disable\": {{dhcp_disable}},\n            \"source-interface\": \"{{source_interface}}\",\n            \"source-vlan\": {{source_vlan}},\n            \"time-serve\": [{{time_serve}}],\n            \"traps\": [\"{{traps}}\"],\n            \"servers\": [\n                {\n                    \"address\": \"{{server_address}}\",\n                    \"tx-mode\": \"{{tx_mode}}\",\n                    \"burst\": \"{{burst}}\",\n                    \"iburst\": \"{{iburst}}\",\n                    \"key-identifier\": {{server_key_identifier}},\n                    \"max-poll\": {{max_poll}},\n                    \"min-poll\": {{min_poll}},\n                    \"mgmt-interface\": {{mgmt_interface}},\n                    \"prefer\": {{prefer}},\n                    \"version\": {{server_version}}\n                }\n            ],\n            \"max-association\": {{max_association}},\n            \"operation-mode\": \"{{operation_mode}}\",\n            \"server-mode-disable\": {{server_mode_disable}},\n            \"name\": \"{{profile_name}}\",\n            \"description\": \"{{profile_description}}\",\n            \"vrf\": \"{{vrf}}\"\n        }\n    ]\n}"
            "options": {
              "raw": {
                "language": "json"
              }
            }
        },
        "url": {
              "raw": "{{central_api_base_url}}/network-config/v1alpha1/ntp", // This last value should be the API name
              "host": [
                    "{{central_api_base_url}}"
                    ],
              "path": [
                    "network-config",
                    "v1alpha1",
                    "ntp"  // This should be the API name 
                    ],
              "query": [
                {
                    "key": "object_type",
                    "value": "LOCAL",
                    "disabled": true
                },
                {
                    "key": "scope_id",
                    "value": "{{scope_id}}",
                    "description": "ID of scope to create profile",
                    "disabled": true
                },
                {
                    "key": "persona",
                    "value": "{{persona}}",
                    "description": "Device function category to create profile under",
                    "disabled": true
                }
              ]
        }
    }
}
```

## 3. Adding the Mandatory Pre-request Script

This script is required to clean up null, empty, or placeholder values:

```json
"event": [
    {
        "listen": "prerequest",
        "script": {
            "exec": [
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
            ],
            "type": "text/javascript"
        }
    }
]
```

## 4. The Final Postman Collection

```json
{
   
    "name": "NTP",
    "item": [
        {
            "name": "Create NTP Profile",
            "event": [
                {
                    "listen": "prerequest",
                    "script": {
                        "exec": [
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
                        ],
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
                    "raw": "{\n    \"profile\": [\n        {\n            \"authenticate\": {{authenticate}},\n            \"authentication-profile\": [\n                {\n                    \"key-identifier\": {{key_identifier}},\n                    \"key-hash\": \"{{key_hash}}\",\n                    \"key-value\": \"{{key_value}}\",\n                    \"key-trusted\": {{key_trusted}},\n                    \"ciphertext\": {\n                        \"key-value\": \"{{ciphertext_key_value}}\"\n                    }\n                }\n            ],\n            \"trusted-key\": [{{trusted_key}}],\n            \"conductor\": [\n                {\n                    \"vrf\": \"{{vrf}}\",\n                    \"stratum\": {{stratum}}\n                }\n            ],\n            \"debug\": {{debug}},\n            \"dhcp-disable\": {{dhcp_disable}},\n            \"source-interface\": \"{{source_interface}}\",\n            \"source-vlan\": {{source_vlan}},\n            \"time-serve\": [{{time_serve}}],\n            \"traps\": [\"{{traps}}\"],\n            \"servers\": [\n                {\n                    \"address\": \"{{server_address}}\",\n                    \"tx-mode\": \"{{tx_mode}}\",\n                    \"burst\": \"{{burst}}\",\n                    \"iburst\": \"{{iburst}}\",\n                    \"key-identifier\": {{server_key_identifier}},\n                    \"max-poll\": {{max_poll}},\n                    \"min-poll\": {{min_poll}},\n                    \"mgmt-interface\": {{mgmt_interface}},\n                    \"prefer\": {{prefer}},\n                    \"version\": {{server_version}}\n                }\n            ],\n            \"max-association\": {{max_association}},\n            \"operation-mode\": \"{{operation_mode}}\",\n            \"server-mode-disable\": {{server_mode_disable}},\n            \"name\": \"{{profile_name}}\",\n            \"description\": \"{{profile_description}}\",\n            \"vrf\": \"{{vrf}}\"\n        }\n    ]\n}"
                },
                "url": {
                    "raw": "{{central_api_base_url}}/network-config/v1alpha1/ntp", // This last value should be the API name
                    "host": [
                        "{{central_api_base_url}}"
                    ],
                    "path": [
                        "network-config",
                        "v1alpha1",
                        "ntp" // This should be the API name 
                    ],
                    "query": [
                        {
                            "key": "object_type",
                            "value": "LOCAL",
                            "disabled": true
                        },
                        {
                            "key": "scope_id",
                            "value": "{{scope_id}}",
                            "description": "ID of scope to create profile",
                            "disabled": true
                        },
                        {
                            "key": "persona",
                            "value": "{{persona}}",
                            "description": "Device function category to create profile under",
                            "disabled": true
                        }
                    ]
                }
            },
            "response": []
        }
    ],
    "description": "Matched Lines:"
}
```
