import json
input_file = "Dataset/finetune_data.jsonl"
output_file = "Dataset/converted_chat_dataset.json"

converted = []

with open(input_file, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        conversation = {
            "conversations": [
                {
                    "from": "human",
                    "value": f"{data['instruction']}\n{data['input']}"
                },
                {
                    "from": "gpt",
                    "value": data["output"]
                }
            ]
        }
        converted.append(conversation)

# Save to new JSON file
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(converted, f, indent=2)

print(f"Converted chat-style dataset saved to {output_file}")
