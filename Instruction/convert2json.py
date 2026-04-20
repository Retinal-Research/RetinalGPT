import json
def convert_to_map(text, align=False):
    text = text.replace("*", "")
    lines = text.strip().split("\n")

    # lines = [line.strip() for line in text.replace("\n\n", "\n").split("\n") if line.strip()]

    conversations = []
    
    for line in lines:
        line = line.lstrip()
        if line.startswith("Us"):
            if not "\n<image>" in line[len("User:"):].strip() and align:
                conversations.append({
                    "from": "human",
                    "value": line[len("User:"):].strip() + "\n<image>"
                })
            else:
                conversations.append({
                    "from": "human",
                    "value": line[len("User:"):].strip()
                })
        elif line.startswith("Ass"):
            conversations.append({
                "from": "gpt",
                "value": line[len("Assistant:"):].strip()
            })
    if len(conversations) == 0:
        print("No Convesations")
        return -1
    if not len(conversations) % 2 == 0:
        print("incomplete results")
        return -1
        conversations = conversations[:-1]
    
    return conversations
# 读取文件并转换为嵌套形式
def convert_file_to_nested_format(input_file, output_file):
    nested_data = []  # 用于存储嵌套的结果

    # 逐行读取 JSON 文件
    with open(input_file, "r", encoding="utf-8") as file:
        for line in file:
            # 将每行的 JSON 对象解析为字典
            if line.strip():  # 跳过空行
                item = json.loads(line.strip())
                nested_data.append(item)

    # 将嵌套结果保存到新的 JSON 文件
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(nested_data, file, indent=4, ensure_ascii=False)
