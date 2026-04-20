
from utils import ana_outputs, create_batch
from convert2json import convert_file_to_nested_format
import pandas as pd
from Desc.MessidorDesc import MessidorDesc



# def create_prompt():
#   prompt = f"""
#   You are a professional ophthalmology medical assistant.
#   You will be provided with quantitative analysis of fundus blood vessels, image quality, and Diabetic Retinopathy Severity Level, but all of this information is completely HIDDEN from the user and accessible ONLY to the assistant. 
#   The user is unaware of the existence of these analyses and only knows that there is an image.
#   Your task is to generate a conversation between a person (User) inquiring about the image and you (Assistant) responding to their questions related to the information provided.
#   The conversation should proceed as though both the User and Assistant are viewing the image. But you don't have access to the actual image.
  
#   Below are requirements for conversations:
#   1.The conversation should include at least 3-6 turns of questions and answers about the image. 
#   2.The user should ask questions as a regular person, and it is strictly prohibited to use any professional or technical terms. 
#   3.Each question should reference "image/picture" while remaining open-ended to allow diverse and natural interactions.
#   4.Assistant should use as much information as possible, like values of fundus features, to provide the most professional response. Reveal the relationship between diseases and any fundus features, and identify any abnormalities or potential risks.
#   5.The user's first question should naturally inquire about the image, focusing on abnormalities, health status, features, or significance, and should begin with "<image>". The response should emphasize notable findings and observations with detailed values in the image.
#   6.The user must have no medical background or knowledge and should be unaware of any information about the image, including fundus features and disease-related details. It is strictly prohibited for the user's questions to include any invisible image characteristics or disease labels.
#   7.Ensure that each question is a single question, standalone sentence, consisting of only ONE question itself without any preceding or accompanying statements. The questions should be diverse, focusing on different aspects of the image to maintain variety.
#   8.Avoid overconfidence, medical advice, or diagnoses. Encourage consulting a healthcare professional for guidance.
#   9.Ensure that one question inquires about the modality of the image. 

#   Output:
#     User: <image> Question1
#     Assistant: Answer1
#     User: Question2
#     Assistant: Answer2
#     """
  

#   return prompt

def create_prompt():
  prompt = f"""
  You are a professional ophthalmology medical assistant who possesses private data about a Color Fundus Photograph (CFP). This data includes:
  -Diabetic Retinopathy Severity Level.
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

# image_list = os.listdir('/media/xinli38/T7 Touch/V&T/OIA-ODIR/image_224')
files = pd.read_csv('Messidor/M4/macula_features.csv')
image_list = files.iloc[:,0].tolist()
desc = MessidorDesc(fractal_analysis_csv='frac_analysis/csv_sig/Messidor.csv', 
                 quality_csv='Messidor/results_ensemble.csv', 
                 dr_label_csv='Messidor/train.csv')

asyncio.run(generate_conversations(
  image_list=image_list[1100:1200],
  prompt=create_prompt,
  desc=desc,
  save_path= 'batch_simple/instruction/jsonl/Messidor.jsonl',
  prefix_name='Messidor/',
  ext=', the modality of the image is Color Fundus Photograph'
))
convert_file_to_nested_format('batch_simple/instruction/jsonl/Messidor.jsonl', 'batch_simple/instruction/ins/Messidor.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt,
#         save_path= 'batch_simple/instruction/req/Messidor.jsonl',
#         ext= ', the modality of the image is Color Fundus Photograph'
#         )

# create_batch_file(img_list=image_list, desc=desc)




# alignment

# import asyncio
# from instruction_gen_async import generate_conversations

# # image_list = os.listdir('/media/xinli38/T7 Touch/V&T/OIA-ODIR/image_224')
# files = pd.read_csv('Messidor/M4/macula_features.csv')
# image_list = files.iloc[:,0].tolist()
# desc = MessidorDesc(
#                  quality_csv='Messidor/results_ensemble.csv', 
#                  dr_label_csv='Messidor/train.csv')

# asyncio.run(generate_conversations(
#   image_list=image_list[50:53],
#   prompt=create_prompt_alignment,
#   desc=desc,
#   save_path= 'batch_simple/alignment_test.jsonl',
#   prefix_name='Messidor/',
#   ext=', the modality of the image is Color Fundus Photograph'
# ))
# convert_file_to_nested_format('batch_simple/alignment_test.jsonl', 'batch_simple/alignment_test.json')


# from utils import create_batch

# def create_batch_file(img_list, desc):

#     create_batch(
#         image_list=img_list, 
#         desc = desc,
#         prompt=create_prompt_alignment,
#         save_path= 'batch_simple/alignment/req/Missidor.jsonl',
#         ext= ', the modality of the image is Color Fundus Photograph'
#         )

# create_batch_file(img_list=image_list, desc=desc)