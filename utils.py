import json

def validate_jsonl(file_path):
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            try:
                data = json.loads(line)
                if 'messages' not in data:
                    print(f"Line {line_number}: Missing 'messages' key")
                    return
                messages = data['messages']
                if not isinstance(messages, list):
                    print(f"Line {line_number}: 'messages' is not a list")
                    return
                for message in messages:
                    if not isinstance(message, dict):
                        print(f"Line {line_number}: A message is not a dictionary")
                        return
                    if 'role' not in message or 'content' not in message:
                        print(f"Line {line_number}: Missing 'role' or 'content' key in a message")
                        return
            except json.JSONDecodeError:
                print(f"Line {line_number}: Invalid JSON")
                return
    print("Validation successful: All data conforms to the schema.")

validate_jsonl("train.jsonl")
validate_jsonl("test.jsonl")