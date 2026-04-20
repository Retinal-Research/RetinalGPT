
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.ODIRDDesc import ODIRDDesc

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
  The user will ask all of the following questions list about various aspects of the image, but their order will be randomized:
  -Image Characteristics. Generate either one combined question covering both aspects or two separate questions, each addressing one aspect.
    Modality, 
    Quality. 
  -Diseases or Abnormalities:
  -Vascular Quantitative Analysis:
    The user inquires about Vascular Quantitative Analysis if it is available.
  The order in which these three main questions appear is fully randomized. Ensure diverse phrasing for questions, and NO repetition.  
  The user must not mention or suspect any hidden data (like DR severity, specific numeric measures, advanced medical terms).
  Assistant's Answers:
  Provide concise answers directly based on the hidden data (disease label, vascular analysis, image quality).
  Avoid unnecessary explanations or redundant details.
  When answering a question about vascular quantitative analysis, include multiple specific quantitative values from the hidden information to ensure response diversity. 
  Constraints:
  Ensuring the number of turns varies to maintain diversity.  
  The user's perspective remains that they are simply curious about the “picture.”
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

import asyncio, time
from instruction_gen_async import generate_conversations

# image_list = os.listdir('/media/xinli38/T7 Touch/V&T/OIA-ODIR/image_224')
files = pd.read_csv('frac_analysis/csv_sig/ODIR.csv')
image_list = files.iloc[:,0].tolist()
desc = ODIRDDesc(fractal_analysis_csv='frac_analysis/csv_sig/ODIR.csv',
                 quality_csv='/media/xinli38/T7 Touch/V&T/OIA-ODIR/Results/M1/results_ensemble.csv', 
                 disease_csv='/media/xinli38/T7 Touch/V&T/OIA-ODIR/Training Set/Annotation/training annotation (English).xlsx')

# asyncio.run(generate_conversations(
#   image_list=image_list[405:600],
#   prompt=create_prompt,
#   desc=desc,
#   save_path= 'batch_simple/instruction/jsonl/ODIR.jsonl',
#   prefix_name='ODIR/',
#   ext=', the modality of the image is Color Fundus Photograph'
# ))

image_list = image_list[6000:]
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
                save_path='batch_simple/instruction/jsonl/ODIR.jsonl',
                prefix_name='ODIR/',
                ext=', the modality of the image is Color Fundus Photograph'
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
        print("Sleeping for 3 seconds before the next batch...")
        await asyncio.sleep(3)  # 休眠 5 秒，防止服务器拒绝请求

# 运行完整任务
asyncio.run(main())

# 处理完所有 batch 后，转换格式
convert_file_to_nested_format('batch_simple/instruction/jsonl/ODIR.jsonl', 'batch_simple/instruction/ins/ODIR.json')







# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list[6200:], 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= 'batch_new/batch_req/ODIR_6200-.jsonl',
#         ext=', the modality of the image is Color Fundus Photograph'
#         )

# create_batch_file(img_list=image_list, desc=desc)




# Alignment
# asyncio.run(generate_conversations(
#   image_list=image_list[:10],
#   prompt=create_prompt_alignment,
#   desc=desc,
#   save_path= 'batch_simple/alignment_test.jsonl',
#   prefix_name='ODIR/',
#   ext=', the modality of the image is Color Fundus Photograph'
# ))
# convert_file_to_nested_format('batch_simple/alignment_test.jsonl', 'batch_simple/alignment_test.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt_alignment,
#         save_path= 'batch_simple/alignment/req/ODIR.jsonl',
#         ext=', the modality of the image is Color Fundus Photograph'
#         )

# create_batch_file(img_list=image_list, desc=desc)

