
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.AlignDesc import AlignDesc


def create_prompt(image_description=None):
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


def unpakced_output():
    batch_path = '/media/xinli38/T7 Touch/V&T/batchs/outputs/batch_6755ea8babb08191b6b03f62fcd06e71_output.jsonl'
    sava_path = "/media/xinli38/T7 Touch/V&T/batchs/json_list/ODIR.jsonl"
    instruction_save = '/media/xinli38/T7 Touch/V&T/batchs/instructions/instruction_ODIR.json'
    ana_outputs(input_path=batch_path, save_path=sava_path,prefix_name="ODIR", align=True)
    convert_file_to_nested_format(sava_path, instruction_save)


def create_batch_file():
    files = pd.read_csv('Results_APTOS/M4/disc_features.csv')
    image_list = files.iloc[:,0].tolist()
    create_batch(
        image_list=image_list, 
        desc = AlignDesc(
            fractal_analysis_csv='Results_APTOS/M4/disc_features.csv', 
            quality_csv='Results_APTOS/M1/results_ensemble.csv',
            dr_label_csv='APTOS/train.csv'
        ), 
        prompt=create_prompt,
        img_path = "APTOS/train/",
        save_path= "/media/xinli38/T7 Touch/V&T/batchs/inputs/APTOS.jsonl"
        )
create_batch_file()

# unpakced_output()