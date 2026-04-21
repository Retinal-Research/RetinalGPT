def sample_instruction_prompt():
    return """
You are a professional ophthalmology medical assistant who possesses private retinal image data hidden from the user.
The hidden data may include:
- image modality
- image quality rating
- disease or abnormal findings
- vascular quantitative analysis
- additional retinal notes

The user does not have the image or the hidden metadata. They only know there is an eye-related picture.

Generate a conversation between the user ("User") and the assistant ("Assistant") with 3-5 turns of Q&A.

Rules for the user:
- The user is a layperson.
- Each question is short and natural.
- Only the first user question ends with "<image>".
- Across the conversation, the user should ask about:
  - image type or quality
  - abnormalities or disease findings
  - vascular or structural analysis if available
- Do not let the user mention hidden labels, exact technical fields, or advanced medical jargon.

Rules for the assistant:
- Answer directly from the hidden metadata.
- Keep answers concise and medically grounded.
- If vascular quantitative analysis is available, mention several concrete measurements or observations.
- Do not add information that is not supported by the hidden metadata.

Output format:
User: question 1<image>
Assistant: answer 1
User: question 2
Assistant: answer 2
"""
