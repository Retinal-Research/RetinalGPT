import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
from utils import convert_file_to_nested_format
from Desc.EyeQDesc import EyeQDesc

def create_prompt(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Diabetic Retinopathy Severity Level label. But the Diabetic Retinopathy Severity Level label is not visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with DR levels.
    - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

  return prompt

image_list = ['12802_right.png', '12829_left.png', '12829_right.png', '12837_right.png', '12839_left.png', '12856_right.png', '12864_left.png', '12877_left.png', '25829_right.png','2582_left.png','25875_left.png','25893_right.png','26006_left.png','26007_right.png','28296_right.png','28307_left.png','28328_left.png','28333_left.png']
# image_list = ['829_right.png']
# files = pd.read_csv('/media/xinli38/T7 Touch/V&T/EyePACS/good/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()

desc = EyeQDesc(dr_label_csv='/media/xinli38/T7 Touch/EyePACS/Label_EyeQ_good.csv')

asyncio.run(generate_conversations(
  image_list=image_list,
  prompt=create_prompt,
  desc=desc,
  save_path= 'batchs/instructions/loacal/test.jsonl',
  image_path= '/media/xinli38/T7 Touch/EyePACS/good_quality/image_224',
  prefix_name='EyePACS/'
))
# convert_file_to_nested_format('batchs/instructions/loacal/EyeQ.jsonl', 'batchs/instructions/loacal/instruction.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list[6000:], 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= '/media/xinli38/T7 Touch/V&T/batchs/inputs/EyeQ_usable_6000-.jsonl',
#         img_path= '/media/xinli38/T7 Touch/EyePACS/usable_quality/image_224',
#         )

# create_batch_file(img_list=image_list, desc=desc)
