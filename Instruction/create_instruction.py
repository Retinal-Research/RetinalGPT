import os,json
from utils import ana_outputs
from convert2json import convert_file_to_nested_format
import pandas as pd
path = 'batch_simple/instruction/res/RFMiD'

# files = os.listdir(path)
# for file in files:
#     print(file)
#     ana_outputs(os.path.join(path, file),'batch_simple/instruction/jsonl/RFMiD_train.jsonl','RFMiD_train/')

# convert_file_to_nested_format('batch_new/jsonl/EyePACS.jsonl', 'batch_new/ins/EyePACS.json')
import json

def validate_json_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            try:
                item = json.loads(line.strip())  # 解析每一行 JSON
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format on line {line_number}.")
                continue
            
            conversations = item.get("conversations", [])
            
            if not conversations:
                print(f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) has no conversations.")
                continue

            for i, conv in enumerate(conversations):
                from_value = conv.get("from")
                value = conv.get("value")

                # 确保 `from` 和 `value` 都不为空
                if not from_value or not value:
                    print(f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) has an empty conversation at index {i}.")

                # 检查 `<image>` 规则
                if i == 0:
                    if not value.endswith("<image>"):
                        print(f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) - First question must end with '<image>'.")
                else:
                    if "<image>" in value:
                        print(f"Error: Line {line_number} (ID: {item.get('id', 'Unknown')}) - Question at index {i} should not contain '<image>'.")

import re

def fix_json_lines(file_path, output_file_path):
    with open(file_path, "r", encoding="utf-8") as f, open(output_file_path, "w", encoding="utf-8") as out_f:
        for line_number, line in enumerate(f, start=1):
            try:
                item = json.loads(line.strip())  # 解析 JSON
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON format on line {line_number}. Skipping.")
                continue
            
            conversations = item.get("conversations", [])
            
            if not conversations:
                print(f"Warning: Line {line_number} (ID: {item.get('id', 'Unknown')}) has no conversations.")
                out_f.write(json.dumps(item, ensure_ascii=False) + "\n")
                continue

            # 修正第一条 `human` 的问题
            if conversations[0]["from"] == "human":
                first_question = conversations[0]["value"]
                if not first_question.endswith("<image>"):
                    print(f"Fixing: Line {line_number} (ID: {item.get('id', 'Unknown')}) - Adding '<image>' to the first question.")
                    conversations[0]["value"] += "<image>"

            # 修正后续 `human` 的问题，移除 `<image>`
            for i in range(1, len(conversations)):
                if conversations[i]["from"] == "human" and "<image>" in conversations[i]["value"]:
                    print(f"Fixing: Line {line_number} (ID: {item.get('id', 'Unknown')}) - Removing '<image>' from question at index {i}.")
                    conversations[i]["value"] = re.sub(r"<image>", "", conversations[i]["value"]).strip()

            # 写入修正后的 JSON 行
            out_f.write(json.dumps(item, ensure_ascii=False) + "\n")


def merge_jsonl_files(input_file, output_file):
    """
    Merge multiple JSONL files into a single JSONL file.

    Args:
        input_files (list of str): List of input JSONL file paths.
        output_file (str): Path of the output JSONL file.
    """
    with open(output_file, 'a', encoding='utf-8') as outfile:
        with open(input_file, 'r', encoding='utf-8') as infile:
            for line in infile:
                outfile.write(line)
            print(input_file)

output_file = 'batch_simple/instruction/jsonl/all.jsonl'
new_output = 'batch_simple/instruction/jsonl/all_fixed.jsonl'
# merge_jsonl_files('batch_simple/instruction/jsonl/UK.jsonl', output_file)
# validate_json_lines(new_output)
# fix_json_lines(output_file, new_output)
convert_file_to_nested_format('batch_simple/instruction/jsonl/all_fixed.jsonl', 'batch_simple/instruction/ins/all.json')



# # 文件路径
# jsonl_file = "batch_new/jsonl/train_tmp.jsonl"  # 替换为你的 JSONL 文件路径
# csv_file = "batch_new/csv/test_i&F.csv"  # 替换为你的 CSV 文件路径，CSV 中包含 id 列
# test_output_file = "batch_new/jsonl/test_tmp.jsonl"  # 输出测试集文件
# train_output_file = "batch_new/jsonl/train.jsonl"  # 输出训练集文件

# # 读取 CSV 文件，获取测试集的 ID 列
# test_ids = set(pd.read_csv(csv_file)['id'].astype(str))  # 确保 ID 为字符串类型

# # 打开 JSONL 文件，进行筛选
# with open(jsonl_file, 'r') as jsonl_input, \
#      open(test_output_file, 'w') as test_output, \
#      open(train_output_file, 'w') as train_output:
    
#     for line in jsonl_input:
#         record = json.loads(line.strip())  # 将每一行 JSONL 数据加载为字典
#         img_id = str(record['image']).split('.')[0]
#         if img_id in test_ids:
#             json.dump(record, test_output)
#             test_output.write('\n')  # 写入 test.jsonl 文件
#         else:
#             json.dump(record, train_output)
#             train_output.write('\n')  # 写入 train.jsonl 文件

# print(f"筛选完成：测试集存储到 {test_output_file}，训练集存储到 {train_output_file}")