import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
from utils import convert_file_to_nested_format
from Desc.RFMiDDesc import RFMiDDesc
import os

def create_prompt(image_description=None):
    prompt = f"""
        You are a ophthalmologist.
        Provided an image and its corresponding disease information, but the disease information NOT visible to the user.
        Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the provided image, highlighting any noteworthy fundus features and abnormalities.
        Please ensure the output adheres to these instructions:
        -If abnormalities are observed, describe the specific findings and analyze them in conjunction with the provided disease information.
        -Avoid using first-person pronouns such as 'my' or 'I' in the questions.
        -Keep the response within 50 words for conciseness.
        Output:
        User: [Question] <image>
        Assistant: [Answer]
    """

    return prompt

image_list = os.listdir('/media/xinli38/T7 Touch/V&T/RFMiD/1. Original Images/test/image')
# files = pd.read_csv('/media/xinli38/T7 Touch/V&T/EyePACS/usable/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()
desc = RFMiDDesc(disease_csv='/media/xinli38/T7 Touch/V&T/RFMiD/2. Groundtruths/c. RFMiD_Testing_Labels.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[:10],
#   prompt=create_prompt,
#   desc=desc,
#   save_path= 'batchs/instructions/loacal/test.jsonl',
#   image_path= '/media/xinli38/T7 Touch/V&T/RFMiD/1. Original Images/train/image',
#   prefix_name='RFMiD_train/'
# ))
# convert_file_to_nested_format('batchs/instructions/loacal/test.jsonl', 'batchs/instructions/test.json')


from utils import create_batch

def create_batch_file(img_list, desc):

    create_batch(
        image_list=img_list, 
        desc = desc,
        prompt=create_prompt,
        save_path= '/media/xinli38/T7 Touch/V&T/batchs/inputs/RFMiD_test.jsonl',
        img_path= '/media/xinli38/T7 Touch/V&T/RFMiD/1. Original Images/test/image',
        )

create_batch_file(img_list=image_list, desc=desc)

