from convert2json import convert_file_to_nested_format
import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio
import base64




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

files = pd.read_csv('OIA-ODIR/Results/M4/macula_features.csv')
image_list = files.iloc[:,0].tolist()
asyncio.run(generate_conversations(image_list[40:50], create_prompt, type='align'))
convert_file_to_nested_format('conversations.json', 'instruction.json')
