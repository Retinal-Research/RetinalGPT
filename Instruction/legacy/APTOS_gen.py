from convert2json import convert_to_map, convert_file_to_nested_format
import pandas as pd
from instruction_gen_async import generate_conversations
import asyncio


def create_prompt(image_description):
    prompt = f"""
  You will receive a description for a fundus retinal image, includes an analysis of the vessels, an image quality, and whether the image is indicative of disease and disease type.
  You will not see the actual image and can only rely on the provided information for your response.
  Your task is to generate a conversation between a person (User) inquiring about the image and you (Assistant) responding to their questions.
  The conversation should proceed as though both the User and Assistant are viewing the image, answer related to the descptions.

  Input: "{image_description}"
  Output:
    User: [Insert Question 1]
    Assistant: [Insert Answer 1]

  Below are requirements for conversations:
  - Based on the provided information, conduct a question-and-answer discussion about the visual features of the retinal fundus image, including but not limited to the blood vessel morphology, image quality, and possible signs of disease.
  - Ensure that the questions are diverse and cover various aspects of the image's visual features based on the provided information.
  - Conversations should include 5-6 turns of questions and answers on image features. Simulate a user uploading an image, where a medical assistant provides answers based on the image information and the provided information(Input).
  - Answer responsibly, avoid overconfidence, and do not provide medical advice or diagnostic information. Encourage the user to consult a healthcare professional for advice.
    """
    return prompt


def main():
    files = pd.read_csv("/path/to/Results_APTOS/M4/disc_features.csv")
    image_list = files.iloc[:, 0].tolist()
    asyncio.run(generate_conversations(image_list[:20]), create_prompt())


if __name__ == "__main__":
    main()
