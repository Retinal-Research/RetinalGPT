
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.AlignDesc import AlignDesc


def create_prompt(image_description=None):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with an image and a Diabetic Retinopathy Severity Level. But the Diabetic Retinopathy Severity Level is not visible to the user.
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


def unpakced_output():
    batch_path = '/media/xinli38/T7 Touch/V&T/batchs/outputs/APTOS/batch_6756bf87fcc48191b159452299e3a843_output.jsonl'
    sava_path = "/media/xinli38/T7 Touch/V&T/batchs/json_list/APTOS.jsonl"
    instruction_save = '/media/xinli38/T7 Touch/V&T/batchs/instructions/instruction_APTOS.json'
    ana_outputs(input_path=batch_path, save_path=sava_path,prefix_name="APTOS", align=True)
    convert_file_to_nested_format(sava_path, instruction_save)


def create_batch_file():
    files = pd.read_csv('Results_APTOS/M4/macula_features.csv')
    image_list = files.iloc[:,0].tolist()

    import os
    import json
    files = pd.read_csv('APTOS/train.csv')
    label_0 = files[files.iloc[:,1] == 0].iloc[:,0].tolist()
    print(len(label_0))
    img_list = []
    for img in label_0:
       img_list.append(f"{img}.png")


    create_batch(
        image_list=img_list, 
        desc = AlignDesc(
            fractal_analysis_csv='Results_APTOS/M4/macula_features.csv', 
            quality_csv='Results_APTOS/M1/results_ensemble.csv',
            dr_label_csv='APTOS/train.csv'
        ), 
        prompt=create_prompt,
        img_path = "APTOS/train/",
        save_path= "/media/xinli38/T7 Touch/V&T/batchs/inputs/APTOS_0.jsonl"
        )

create_batch_file()


# files = os.listdir('batchs/outputs/APTOS')
# for file in files:
#     file_path = os.path.join('batchs/outputs/APTOS', file)

#     # 读取文件内容
#     with open(file_path, 'r', encoding='utf-8') as f:
#         lines = f.readlines()
#     updated_lines = []
#     for line in lines:
#         try:
#             data = json.loads(line)  # 每一行解析为 JSON 对象
#             if data.get("custom_id") not in label_0:
#                 updated_lines.append(line)  # 保留不需要删除的行
#         except json.JSONDecodeError:
#             # 如果行解析失败，保留原行
#             updated_lines.append(line)

#     # 写回文件
#     with open(file_path, 'w', encoding='utf-8') as f:
#         f.writelines(updated_lines)
# # # create_batch_file()
# # unpakced_output()