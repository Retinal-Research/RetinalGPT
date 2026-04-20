
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.IDRIDDesc import IDRIDDesc


def create_prompt():
  prompt = f"""
  You are a professional ophthalmology medical assistant who possesses private data about a Color Fundus Photograph (CFP). This data includes:
  -Quantitative vascular analysis results.
  -An image quality rating.
  -Bounding box data for anomalies or lesions. The bounding box format is as follows: anomalies or lesions type: [x_min, y_min, x_max, y_max]... ...
  All these details are hidden from the user. The user does not have the CFP or its technical information; they only know it's some sort of eye-related image.

  You must generate a conversation between the user (“User”) and you (“Assistant”), adhering to the following rules:

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
  The user will inquire about lesions, specifically regarding severity or location.
  The User do NOT repeatedly inquire about the same aspects. 
  The user must not mention or suspect any hidden data (like DR severity, specific numeric measures, advanced medical terms).
  Assistant's Answers:
  Provide concise answers directly based on the hidden data (disease label, vascular analysis, image quality).
  Avoid unnecessary explanations or redundant details.
  When answering a question about vascular quantitative analysis, include multiple specific quantitative values from the hidden information to ensure response diversity. 
  When answering the question about lesions, response should use the provided bounding box information to describe the lesion, like presence, approximate size, and position within the image (e.g., near the macula, optic disc, or peripheral retina).
  Constraints:
  The conversation consist of 3-6 turns of Q&A, ensuring the number of turns varies to maintain diversity.  
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




import asyncio, os
from instruction_gen_async import generate_conversations

files = pd.read_csv('frac_analysis/csv_sig/IDRID_seg.csv')
image_list = files.iloc[:,0].tolist()
desc = IDRIDDesc(fractal_analysis_csv='frac_analysis/csv_sig/IDRID_seg.csv', quality_csv='Results_IDRID_seg/M1/results_ensemble.csv', bd_path='IDRID/bounding_boxes.json')

asyncio.run(generate_conversations(
  image_list=image_list[10:],
  prompt=create_prompt,
  desc=desc,
  ext= 'The modality of the image is Color Fundus Photograph',
  save_path= 'batch_simple/instruction/jsonl/IDRID_seg.jsonl',
  prefix_name='IDRID_seg/',
))
convert_file_to_nested_format('batch_simple/instruction/jsonl/IDRID_seg.jsonl', 'batch_simple/instruction/ins/IDRID_seg.json')

# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= 'batch_new/batch_req/IDRID_seg.jsonl',
#         ext= 'The modality of the image is Color Fundus Photograph'
#         )

# create_batch_file(img_list=image_list, desc=desc)




# # Alignment
# files = pd.read_csv('frac_analysis/csv_sig/IDRID_seg.csv')
# image_list = files.iloc[:,0].tolist()
# desc = IDRIDDesc(quality_csv='Results_IDRID_seg/M1/results_ensemble.csv')

# # asyncio.run(generate_conversations(
# #   image_list=image_list[70:80],
# #   prompt=create_prompt_alignment,
# #   desc=desc,
# #   ext= ', The modality of the image is Color Fundus Photograph, the image contain signs of diabetic retinopathy',
# #   save_path= 'batch_simple/alignment_test.jsonl',
# #   prefix_name='IDRID_seg/',
# # ))
# # convert_file_to_nested_format('batch_simple/alignment_test.jsonl', 'batch_simple/alignment_test.json')

# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt_alignment,
#         save_path= 'batch_simple/alignment/req/IDRID_seg.jsonl',
#         ext= ', The modality of the image is Color Fundus Photograph, the image contain signs of diabetic retinopathy',
#         )

# create_batch_file(img_list=image_list, desc=desc)