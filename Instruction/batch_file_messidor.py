import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
from utils import convert_file_to_nested_format
from Desc.MessidorDesc import MessidorDesc

def create_prompt(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with an image and a Diabetic Retinopathy Severity Level(0,1,2,3). But the Diabetic Retinopathy Severity Level is not visible to the user.
    Your task is to create a single round of medical instruction and a dialog where the user addresses the content of the image user provided, highlighting any notable fundus features and abnormalities.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with DR levels.
    - Similar to a patient consultation.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

  return prompt


files = pd.read_csv('Messidor/M4/macula_features.csv')
image_list = files.iloc[:,0].tolist()

desc = MessidorDesc(dr_label_csv='Messidor/train.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[:15],
#   prompt=create_prompt,
#   desc=desc,
#   save_path= 'batchs/instructions/loacal/conversations.jsonl',
#   image_path= 'Messidor/image',
#   prefix_name='Messidor/'
# ))
# convert_file_to_nested_format('batchs/instructions/loacal/conversations.jsonl', 'batchs/instructions/loacal/instruction.json')

from utils import create_batch

def create_batch_file(img_list, desc):

    create_batch(
        image_list=img_list, 
        desc = desc,
        prompt=create_prompt,
        img_path = "Messidor/image",
        save_path= "/media/xinli38/T7 Touch/V&T/batchs/inputs/Messidor_0-1500.jsonl"
        )

create_batch_file(img_list=image_list, desc=desc)
