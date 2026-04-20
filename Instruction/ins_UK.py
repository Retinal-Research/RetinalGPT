
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.UKDesc import UKDesc


# def create_prompt():
#   prompt = f"""
#   You are a professional ophthalmology medical assistant.
#   You are provided with quantitative analysis of fundus blood vessels, image quality, and disease information. All of this information is completely HIDDEN from the user and accessible ONLY to the assistant.
#   Your task is to generate a conversation between a person (User) asking about the image and you (Assistant) answering their questions based on the provided information. 
#   The conversation should simulate both the User and Assistant viewing the image, even though you do not have access to the actual image.
#   Below are requirements for conversations:
#   1.Conversations include 3-6 turns of Q&A about the image. 
#   2.The user should ask questions as a regular person, and it is strictly prohibited to use any professional or technical terms. 
#   3.Each question reference "image/picture" while remaining open-ended to allow diverse and natural interactions.
#   4.Assistant should use as much information as possible, like values of fundus features, to provide the most professional response. Reveal the relationship between diseases and any fundus features, and identify any abnormalities or potential risks.
#   5.The user's first question naturally inquires about the image, focusing on features, significance, health status, or abnormalities, and begins with "<image>". The response emphasizes notable findings and observations with detailed values from the image.
#   6.The user has no medical background or knowledge and is unaware of any information about the image, including fundus features and disease-related details. The user's questions must not include any invisible image characteristics or disease labels and other information provided.
#   7.Each question is a single question, standalone sentence, consisting of only ONE question itself without any preceding or accompanying statements. The questions should be diverse, focusing on different aspects of the image to maintain variety.
#   8.Avoid overconfidence, medical advice, or diagnoses. Encourage consulting a healthcare professional for guidance.
#   9.One question inquires about the modality of the image. 
#   Output Samples:
#     User: <image> Question1
#     Assistant: Answer1
#     User: Question2
#     Assistant: Answer2
#     """
  

#   return prompt




def create_prompt():
  prompt = f"""
  You are a professional ophthalmology medical assistant who possesses private data about a Color Fundus Photograph (CFP). This data includes:
  -Disease information.
  -Quantitative vascular analysis results.
  -An image quality rating.
  All these details are hidden from the user. The user does not have the CFP or its technical information; they only know it's some sort of eye-related image.
  You must generate a conversation between the user (“User”) and you (“Assistant”) with 3-6 turns of Q&A, adhering to the following rules:
  User's Questions:
  The user is a layperson with no medical or technical background.
  Each of their questions is a single, short sentence referencing the “image” or “picture.”
  Only the first question ends with "<image>".
  The user will ask all of the following questions list about 3 aspects of the image:
  1.Image Characteristics(two sub-aspects: Modality, Quality): Generate either one combined question covering both aspects or two separate questions, each addressing one aspect.
  2.Diseases or Abnormalities.
  3.Vascular Quantitative Analysis: The user inquires about Vascular Quantitative Analysis if it is available, generating one or more questions related to Vascular Quantitative Analysis.
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

files = pd.read_csv('Results_VD/M4/macula_features.csv')
image_list = files.iloc[:,0].tolist()
desc = UKDesc(fractal_analysis_csv='frac_analysis/csv_sig/UK_VD.csv', quality_csv='Results_VD/M1/results_ensemble.csv')

asyncio.run(generate_conversations(
  image_list=image_list[300:],
  prompt=create_prompt,
  desc=desc,
  # ext= ",this image has Alzheimer's disease, the modality of the image is Color Fundus Photograph",
  ext= ",this image has vascular dementia, the modality of the image is Color Fundus Photograph",
  save_path= 'batch_simple/instruction/jsonl/UK.jsonl',
  prefix_name='UK/'
))
convert_file_to_nested_format('batch_simple/instruction/jsonl/UK.jsonl', 'batch_simple/instruction/ins/UK.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= 'batch_new/batch_req/UK_AD.jsonl',
#         ext= ",this image has Alzheimer's disease, the modality of the image is Color Fundus Photograph",
#         )

# create_batch_file(img_list=image_list, desc=desc)






# Alignment
# files = pd.read_csv('Results_VD/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()
# desc = UKDesc(quality_csv='Results_VD/M1/results_ensemble.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[10:15],
#   prompt=create_prompt,
#   desc=desc,
#   ext= ",this image has vascular dementia, the modality of the image is Color Fundus Photograph",
#   save_path= 'batch_new/jsonl/test.jsonl',
#   prefix_name='UK/'
# ))
# convert_file_to_nested_format('batch_new/jsonl/test.jsonl', 'batch_new/ins/test.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt_alignment,
#         save_path= 'batch_simple/alignment/req/VD.jsonl',
#         # ext= ",this image has Alzheimer's disease, the modality of the image is Color Fundus Photograph",
#         # ext= ",this image has Parkinson's disease, the modality of the image is Color Fundus Photograph",
#         ext= ",this image has vascular dementia, the modality of the image is Color Fundus Photograph",
#         )

# create_batch_file(img_list=image_list, desc=desc)
