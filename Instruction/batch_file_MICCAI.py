import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
from utils import convert_file_to_nested_format
from Desc.MICCAIDesc import MICCAIDesc
import os

def create_prompt_LT(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Lesion Types in Myopic Maculopathy. But the Lesion Types is NOT visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the image provided, highlighting any fundus features.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings and fundus features releated to the Myopic Maculopathy Type.
    - Questions should in various ways in fundus features and eyes health status. Questions DO NOT focus on the image details.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

  return prompt

def create_prompt_MM(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Myopic Maculopathy Grading label. But the grading label is NOT visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the image provided, highlighting any fundus features.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings and fundus features releated to the Myopic Maculopathy.
    - Questions should in various ways in fundus features and eyes health status. Questions DO NOT focus on the image details.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

  return prompt

image_list = os.listdir('/media/xinli38/T7 Touch/V&T/Results_MICCAI_task2/M0/images')
# files = pd.read_csv('/media/xinli38/T7 Touch/V&T/EyePACS/usable/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()
desc = MICCAIDesc()

# asyncio.run(generate_conversations(
#   image_list=image_list[50:60],
#   prompt=create_prompt,
#   desc=desc,
#   save_path= 'batchs/instructions/loacal/MICCAI.jsonl',
#   image_path= '/media/xinli38/T7 Touch/V&T/MICCAI/Images/image',
#   prefix_name='MICCAI/'
# ))
# convert_file_to_nested_format('batchs/instructions/loacal/MICCAI.jsonl', 'batchs/instructions/instruction_MICCAI.json')


from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list[0:1500], 
#         desc = desc,
#         prompt=create_prompt_MM,
#         save_path= '/media/xinli38/T7 Touch/V&T/batchs/inputs/MICCAI_0-1500.jsonl',
#         img_path= '/media/xinli38/T7 Touch/V&T/MICCAI/Images/image',
#         )

# create_batch_file(img_list=image_list, desc=desc)


def create_batch_file(img_list, desc):

    create_batch(
        image_list=img_list, 
        desc = desc,
        prompt=create_prompt_LT,
        save_path= '/media/xinli38/T7 Touch/V&T/batchs/inputs/MICCAI_task2.jsonl',
        img_path= '/media/xinli38/T7 Touch/V&T/Results_MICCAI_task2/M0/images',
        )

create_batch_file(img_list=image_list, desc=desc)