import json

# Load original chat-style JSON
with open("Dataset/converted_chat_dataset.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Strict prompt template
prompt_template = """You are a classification assistant.
Classify the text into JSON with two fields:
- "type": exact class label
- "task_group": relevant functional group
Only return JSON.

Input: {input}
"""

converted_data = []

for item in raw_data:
    conversations = item["conversations"]
    
    # Extract and clean user input
    original_input = conversations[0]["value"].split("description.", 1)[-1].strip()
    
    # Extract and format output
    lines = conversations[1]["value"].splitlines()
    type_val = lines[0].replace("Type: ", "").strip()
    task_group_val = lines[1].replace("Task Group: ", "").strip()

    # Convert to pretty-printed JSON string
    gpt_json_str = json.dumps({
        "type": type_val,
        "task_group": task_group_val
    }, indent=2)

    # Construct new conversation entry
    new_item = {
        "conversations": [
            {
                "from": "human",
                "value": prompt_template.format(input=original_input)
            },
            {
                "from": "gpt",
                "value": gpt_json_str  # As string
            }
        ]
    }

    converted_data.append(new_item)

# Save to file
with open("converted_chat_format.json", "w", encoding="utf-8") as f:
    json.dump(converted_data, f, indent=2)
