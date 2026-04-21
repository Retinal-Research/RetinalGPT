import os
import json
from tqdm import tqdm
import pandas as pd
import base64
from convert2json import convert_to_map, convert_file_to_nested_format
try:
    from Desc.base_description import BaseDescription
except ImportError:
    try:
        from .Desc.base_description import BaseDescription
    except ImportError:
        from base_description import BaseDescription

def create_prompt(image_description):
  prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with an image and known diseases of the image. But the disease information is not visible to the user.
    Your task is to create a single round of medical instruction and a dialog where the user addresses the content of the image user provided, highlighting any notable fundus features, abnormalities, or diagnostic insights.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings such as hemorrhages, exudates, microaneurysms, or other pathological changes on the image.
    - Include any possible clinical implications or suspected conditions (e.g., diabetic retinopathy, macular degeneration, glaucoma).
    - Similar to a patient consultation.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """

  return prompt


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def create_batch(image_list=[], desc=None, prompt=None, img_path=None, save_path=None, ext=""):
    for image in tqdm(image_list):
        if not isinstance(desc, BaseDescription):
            return None
        if not prompt:
            return None
        img_desc = desc.get_description(file_name=image)
        if img_desc == "":
            print(f"Skip {image} because of the missing fractal analysis values")
            continue
        img_desc += ext
        if img_path:
            base64_image = encode_image(os.path.join(img_path, image))
            messages=[
                {"role": "system", 
                "content": prompt()
                },
                {"role": "user", "content": img_desc,
                    "type": "image_url",
                    "image_url": {
                        "url":  f"data:image/png;base64,{base64_image}"
                    }
                },
            ]
        else:
            messages=[
                {"role": "system", 
                "content": prompt()
                },
                {"role": "user", "content": img_desc},
            ]
        res = {"custom_id": f"{image.split('.')[0]}", "method": "POST", "url": "/v1/chat/completions", "body" : {"model":"gpt-4o-mini", "messages" : messages}}
        with open(save_path, "a", encoding="utf-8") as file: 
                json.dump(res, file, ensure_ascii=False)
                file.write("\n") 
                file.flush() 

def ana_outputs(input_path="", save_path="", prefix_name="", align=False):
    with open(input_path, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():  # 跳过空行
                item = json.loads(line.strip())
                res = item['response']['body']['choices'][0]['message']['content']
                data = convert_to_map(res, align=align)
                if data == -1:
                    continue
                id = item['custom_id']
                with open(save_path, "a", encoding="utf-8") as file: 
                    file.write(json.dumps(
                        {"id": id, "image": f"{prefix_name}{id}.png", "conversations": data}, 
                        ensure_ascii=False) + "\n"
                    )
