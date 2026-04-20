from convert2json import convert_file_to_nested_format
import pandas as pd
from instruction_gen_async import generate_conversations
from instruction_gen import generate_text
import asyncio, json, os




def create_prompt():
  prompt = f"""
    You are a ophthalmologist.
    Your task is to analyze the provided CFP (Color Fundus Photography) image and determine whether there are any signs of disease or abnormalities. \n\n
    Human: Hi!\n\n
    Assistant: Hi there!  How can I help you today?

  """
  

  return prompt


file_path = '/media/xinli38/T7 Touch/V&T/LLaVA-Med-1.0.0/test.json'
with open(file_path, "r", encoding="utf-8") as f:
    data = json.load(f)
    for item in data:
        id = item['image']


        result = generate_text(
                    prompt=create_prompt,
                    question='Does this image show any diseases?',
                    # save_path= '/media/xinli38/T7 Touch/V&T/LLaVA-Med-1.0.0/test_out_gpt.jsonl',
                    image_path= os.path.join('/media/xinli38/T7 Touch/V&T/LLaVA-Med-1.0.0/dataset', id)
                    )
        print(result)
        break
        # convert_file_to_nested_format('conversations.json', 'instruction.json')
