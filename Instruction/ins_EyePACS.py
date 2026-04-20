
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.EyeQDesc import EyeQDesc
import os

def create_prompt():
  prompt = f"""
  You are a professional ophthalmology medical assistant who possesses private data about a Color Fundus Photograph (CFP). This data includes:
  -The Diabetic Retinopathy (DR) severity level.
  -Quantitative vascular analysis results.
  -An image quality rating.
  All these details are hidden from the user. The user does not have the CFP or its technical information; they only know it's some sort of eye-related image.
  You must generate a conversation between the user (“User”) and you (“Assistant”) with 3-6 turns of Q&A, adhering to the following rules:
  User's Questions:
  The user is a layperson with no medical or technical background.
  Each of their questions is a single, short sentence referencing the “image” or “picture.”
  Only the first question ends with "<image>".
  The user will ask all of the following questions list about various aspects of the image:
  -Image Characteristics(two aspects: Modality, Quality):
    Generate either one combined question covering both aspects or two separate questions, each addressing one aspect.
  -Diseases or Abnormalities.
  -Vascular Quantitative Analysis:
    The user inquires about Vascular Quantitative Analysis if it is available, generating one or more questions related to Vascular Quantitative Analysis.
  Ensure diverse phrasing for questions.
  The User do NOT repeatedly inquire about the same aspects. 
  The user must not mention or suspect any hidden data (like DR severity, specific numeric measures, advanced medical terms).
  Assistant's Answers:
  Provide concise answers directly based on the hidden data (disease label, vascular analysis, image quality).
  Avoid unnecessary explanations or redundant details.
  When answering a question about vascular quantitative analysis, include multiple specific quantitative values from the hidden information to ensure response diversity. 
  Constraints:
  Ensuring the number of turns varies to maintain diversity.  
  No actual image is ever displayed or uploaded.
  Output Samples:
    User:  Question1<image>
    Assistant: Answer1
    User: Question2
    Assistant: Answer2
    """

  return prompt



def create_prompt_alignment():
  prompt = """
  You are a professional ophthalmology medical assistant who possesses private data about a Color Fundus Photograph (CFP). This data includes:
  -The Diabetic Retinopathy (DR) severity level.
  -An image quality rating.
  -Modality of the image.
  All these details are hidden from the user. The user does not have the CFP or its technical information; they only know it's some sort of eye-related image.
  You must generate a conversation between the user (“User”) and you (“Assistant”) with 1 turn of Q&A, adhering to the following rules:
  The user is a layperson with no medical or technical background.
  Naturally inquires about the image. Ensure diverse phrasing for the question. This question end with "\n<image>".
  Using professional medical terminology to answer. Ensure the answer is clear, concise, and medically accurate.
  Questions is a single, short sentence focusing on the “image” or “picture.”
  """
  
  return prompt


import asyncio
from instruction_gen_async import generate_conversations

files = pd.read_csv('frac_analysis/csv_sig/EyeQ_usable.csv')
image_list = files.iloc[:,0].tolist()
desc = EyeQDesc(fractal_analysis_csv='frac_analysis/csv_sig/EyeQ_usable.csv', 
                dr_label_csv='/media/xinli38/T7 Touch/EyePACS/Label_EyeQ_usable.csv')
# desc = EyeQDesc(dr_label_csv='/media/xinli38/T7 Touch/EyePACS/Label_EyeQ_good.csv')
# desc = EyeQDesc(dr_label_csv='/media/xinli38/T7 Touch/EyePACS/Label_EyeQ_usable.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[165:170],
#   prompt=create_prompt,
#   desc=desc,
#   # ext= ", the image is of acceptable with noise, the modality of the image is Color Fundus Photograph",
#   ext= ", this image is of high quality, the modality of the image is Color Fundus Photograph",
#   save_path= 'batch_simple/test.jsonl',
#   prefix_name='EyePACS/'
# ))
# convert_file_to_nested_format('batch_simple/test.jsonl', 'batch_simple/test.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list[12000:14000], 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= 'batch_simple/instruction/req/EyeQ_good_12000-14000.jsonl',
#         ext= ", this image is of high quality, the modality of the image is Color Fundus Photograph"
#         )

# create_batch_file(img_list=image_list, desc=desc)


image_list = image_list[4950:]
batch_size = 50  # 每次最多处理200个

max_retries = 3  # 最大重试次数

async def process_batch(start, end):
    """处理单个批次，带重试机制"""
    for attempt in range(max_retries):
        try:
            print(f"Processing batch {start} to {end}, Attempt {attempt + 1}...")
            
            # 调用 API
            await generate_conversations(
                image_list=image_list[start:end],
                prompt=create_prompt,
                desc=desc,
                save_path='batch_simple/instruction/jsonl/EyePACS_usable.jsonl',
                prefix_name='EyePACS/',
                ext= ", the image is of acceptable with noise, the modality of the image is Color Fundus Photograph",
            )
            
            print(f"Batch {start} to {end} completed successfully.")
            return  # 成功后退出循环
            
        except Exception as e:
            print(f"Error processing batch {start} to {end}: {e}")
            if attempt < max_retries - 1:
                print("Retrying after 10 seconds...")
                await asyncio.sleep(10)  # 休眠 10 秒后重试
            else:
                print("Max retries reached. Skipping this batch.")

async def main():
    """管理所有批次"""
    for i in range(0, len(image_list), batch_size):
        await process_batch(i, min(i + batch_size, len(image_list)))  # 逐批执行
        print("Sleeping for 2 seconds before the next batch...")
        await asyncio.sleep(3)  # 休眠 2 秒，防止服务器拒绝请求

# 运行完整任务
asyncio.run(main())

# 处理完所有 batch 后，转换格式
convert_file_to_nested_format('batch_simple/instruction/jsonl/EyePACS_usable.jsonl', 'batch_simple/instruction/ins/EyePACS.json')





# # Alignment

# files = pd.read_csv('frac_analysis/csv_sig/EyeQ_good.csv')
# image_list = files.iloc[:,0].tolist()
# desc = EyeQDesc(dr_label_csv='/media/xinli38/T7 Touch/EyePACS/Label_EyeQ_good.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[160:175],
#   prompt=create_prompt_alignment,
#   desc=desc,
#   # ext= ", the image is of acceptable with noise, the modality of the image is Color Fundus Photograph",
#   ext= ", this image is of high quality, the modality of the image is Color Fundus Photograph",
#   save_path= 'batch_simple/alignment_test.jsonl',
#   prefix_name='EyePACS/'
# ))
# convert_file_to_nested_format('batch_simple/alignment_test.jsonl', 'batch_simple/alignment_test.json')

# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt_alignment,
#         save_path= 'batch_simple/alignment/req/EyeQ_usable_10000-.jsonl',
#         ext= ", the image is of acceptable with noise, the modality of the image is Color Fundus Photograph",
#         )

# create_batch_file(img_list=image_list, desc=desc)
