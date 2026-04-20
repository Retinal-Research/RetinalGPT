import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
from utils import convert_file_to_nested_format
from Desc.IDRIDDesc import IDRIDDesc
import os

def create_prompt(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and 2 labels of Diabetic Retinopathy Severity Level and Diabetic Macular Edema. But these labels are not visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with provided labels.
    - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

def create_prompt_seg(image_description=None):
    prompt = f"""
        You are a highly experienced ophthalmologist.
        You will be provided with a Retinal Colors Fundus image with Diabetic Retinopathy.
        Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
        Please ensure the output follows these instructions:
        - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with Diabetic Retinopathy.
        - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
        - Keep the response within 50 words for conciseness.
        Output:
        User: [Question] <image>
        Assistant: [Answer]
    """



    return prompt

image_list = os.listdir('/media/xinli38/T7 Touch/V&T/Results_IDRID_seg/M0/images')
# files = pd.read_csv('/media/xinli38/T7 Touch/V&T/EyePACS/usable/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()
desc = IDRIDDesc()

asyncio.run(generate_conversations(
  image_list=image_list,
  prompt=create_prompt_seg,
  desc=desc,
  save_path= 'batchs/instructions/loacal/IDRID_seg.jsonl',
  image_path= '/media/xinli38/T7 Touch/V&T/Results_IDRID_seg/M0/images',
  prefix_name='IDRID_seg/'
))
# convert_file_to_nested_format('batchs/instructions/loacal/IDRID_seg.jsonl', 'batchs/instructions/test.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= '/media/xinli38/T7 Touch/V&T/batchs/inputs/IDRID_test.jsonl',
#         img_path= '/media/xinli38/T7 Touch/V&T/Results_IDRID_test/M0/images',
#         )

# create_batch_file(img_list=image_list, desc=desc)

