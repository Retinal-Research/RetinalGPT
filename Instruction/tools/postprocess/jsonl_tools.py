import argparse
import json
import re

from convert2json import convert_file_to_nested_format


def validate_json_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                item = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format on line {line_number}.")
                continue

            conversations = item.get("conversations", [])
            if not conversations:
                print(f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) has no conversations.")
                continue

            for idx, conversation in enumerate(conversations):
                from_value = conversation.get("from")
                value = conversation.get("value")

                if not from_value or not value:
                    print(
                        f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) "
                        f"has an empty conversation at index {idx}."
                    )

                if idx == 0:
                    if not value.endswith("<image>"):
                        print(
                            f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) "
                            "- First question must end with '<image>'."
                        )
                else:
                    if "<image>" in value:
                        print(
                            f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) "
                            f"- Question at index {idx} should not contain '<image>'."
                        )


def fix_json_lines(file_path, output_file_path):
    with open(file_path, "r", encoding="utf-8") as input_file, open(
        output_file_path, "w", encoding="utf-8"
    ) as output_file:
        for line_number, line in enumerate(input_file, start=1):
            try:
                item = json.loads(line.strip())
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format on line {line_number}. Skipping.")
                continue

            conversations = item.get("conversations", [])
            if not conversations:
                print(f"Warning: Line {line_number} (ID: {item.get('id', 'Unknown')}) has no conversations.")
                output_file.write(json.dumps(item, ensure_ascii=False) + "\n")
                continue

            if conversations[0]["from"] == "human":
                first_question = conversations[0]["value"]
                if not first_question.endswith("<image>"):
                    print(
                        f"Fixing: Line {line_number} (ID: {item.get('id', 'Unknown')}) "
                        "- Adding '<image>' to the first question."
                    )
                    conversations[0]["value"] += "<image>"

            for idx in range(1, len(conversations)):
                if conversations[idx]["from"] == "human" and "<image>" in conversations[idx]["value"]:
                    print(
                        f"Fixing: Line {line_number} (ID: {item.get('id', 'Unknown')}) "
                        f"- Removing '<image>' from question at index {idx}."
                    )
                    conversations[idx]["value"] = re.sub(r"<image>", "", conversations[idx]["value"]).strip()

            output_file.write(json.dumps(item, ensure_ascii=False) + "\n")


def merge_jsonl_files(input_file, output_file):
    with open(output_file, "a", encoding="utf-8") as output, open(
        input_file, "r", encoding="utf-8"
    ) as input_stream:
        for line in input_stream:
            output.write(line)
    print(input_file)


def convert_jsonl_to_nested_json(input_file, output_file):
    convert_file_to_nested_format(input_file, output_file)


def main():
    parser = argparse.ArgumentParser(description="JSONL postprocess helpers.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("file_path")

    fix_parser = subparsers.add_parser("fix")
    fix_parser.add_argument("file_path")
    fix_parser.add_argument("output_file_path")

    merge_parser = subparsers.add_parser("merge")
    merge_parser.add_argument("input_file")
    merge_parser.add_argument("output_file")

    convert_parser = subparsers.add_parser("convert")
    convert_parser.add_argument("input_file")
    convert_parser.add_argument("output_file")

    args = parser.parse_args()

    if args.command == "validate":
        validate_json_lines(args.file_path)
    elif args.command == "fix":
        fix_json_lines(args.file_path, args.output_file_path)
    elif args.command == "merge":
        merge_jsonl_files(args.input_file, args.output_file)
    elif args.command == "convert":
        convert_jsonl_to_nested_json(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
