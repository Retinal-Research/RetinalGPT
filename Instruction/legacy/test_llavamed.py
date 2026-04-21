from convert2json import convert_file_to_nested_format
import json
import os

from instruction_gen import generate_text


def create_prompt():
    prompt = f"""
    You are a ophthalmologist.
    Your task is to analyze the provided CFP (Color Fundus Photography) image and determine whether there are any signs of disease or abnormalities. \n\n
    Human: Hi!\n\n
    Assistant: Hi there!  How can I help you today?

  """
    return prompt


def main():
    file_path = "/path/to/LLaVA-Med-1.0.0/test.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        for item in data:
            image_id = item["image"]
            result = generate_text(
                prompt=create_prompt,
                question="Does this image show any diseases?",
                image_path=os.path.join("/path/to/LLaVA-Med-1.0.0/dataset", image_id),
            )
            print(result)
            break


if __name__ == "__main__":
    main()
