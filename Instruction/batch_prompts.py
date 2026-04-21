def aptos_batch_prompt(image_description=None):
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


def eyeq_batch_prompt(image_description=None):
    prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Diabetic Retinopathy Severity Level label. But the Diabetic Retinopathy Severity Level label is not visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with DR levels.
    - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """
    return prompt


def idrid_batch_prompt(image_description=None):
    prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and 2 labels of Diabetic Retinopathy Severity Level and Diabetic Macular Edema. But these labels are not visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with provided labels.
    - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """
    return prompt


def idrid_seg_batch_prompt(image_description=None):
    prompt = f"""
        You are a highly experienced ophthalmologist.
        You will be provided with a Retinal Colors Fundus image with Diabetic Retinopathy.
        Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the fundus image provided, highlighting any noteworthy fundus features and abnormalities.
        Please ensure the output follows these instructions:
        - If abnormalities are observed, describe the specific findings, and analyzing in conjunction with Diabetic Retinopathy.
        - Similar to consulting an expert. Avoid using first-person pronouns like "my" or "I" in user's question.
        - Keep the response within 50 words for conciseness.
        Output:
        User: [Question] <image>
        Assistant: [Answer]
    """
    return prompt


def miccai_lt_batch_prompt(image_description=None):
    prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Lesion Types in Myopic Maculopathy. But the Lesion Types is NOT visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the image provided, highlighting any fundus features.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings and fundus features releated to the Myopic Maculopathy Type.
    - Questions should in various ways in fundus features and eyes health status. Questions DO NOT focus on the image details.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """
    return prompt


def miccai_mm_batch_prompt(image_description=None):
    prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with a Retinal Colors Fundus image and a Myopic Maculopathy Grading label. But the grading label is NOT visible to the user.
    Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the image provided, highlighting any fundus features.
    Please ensure the output follows these instructions:
    - If abnormalities are observed, describe the specific findings and fundus features releated to the Myopic Maculopathy.
    - Questions should in various ways in fundus features and eyes health status. Questions DO NOT focus on the image details.
    - Keep the response within 50 words for conciseness.
    Output:
    User: [Question] <image>
    Assistant: [Answer]
  """
    return prompt


def odir_batch_prompt(image_description=None):
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


def rfmid_batch_prompt(image_description=None):
    prompt = f"""
        You are a ophthalmologist.
        Provided an image and its corresponding disease information, but the disease information NOT visible to the user.
        Your task is to generate ONE round of conversation between the ophthalmologist and the user based on the provided image, highlighting any noteworthy fundus features and abnormalities.
        Please ensure the output adheres to these instructions:
        -If abnormalities are observed, describe the specific findings and analyze them in conjunction with the provided disease information.
        -Avoid using first-person pronouns such as 'my' or 'I' in the questions.
        -Keep the response within 50 words for conciseness.
        Output:
        User: [Question] <image>
        Assistant: [Answer]
    """
    return prompt


def messidor_batch_prompt(image_description=None):
    prompt = f"""
    You are a highly experienced ophthalmologist.
    You will be provided with an image and a Diabetic Retinopathy Severity Level(0,1,2,3). But the Diabetic Retinopathy Severity Level is not visible to the user.
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


PROMPT_REGISTRY = {
    "aptos_batch_prompt": aptos_batch_prompt,
    "eyeq_batch_prompt": eyeq_batch_prompt,
    "idrid_batch_prompt": idrid_batch_prompt,
    "idrid_seg_batch_prompt": idrid_seg_batch_prompt,
    "miccai_lt_batch_prompt": miccai_lt_batch_prompt,
    "miccai_mm_batch_prompt": miccai_mm_batch_prompt,
    "messidor_batch_prompt": messidor_batch_prompt,
    "odir_batch_prompt": odir_batch_prompt,
    "rfmid_batch_prompt": rfmid_batch_prompt,
}
