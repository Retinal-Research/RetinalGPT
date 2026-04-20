import asyncio
import aiofiles
import json
import base64
import os
import io
import csv
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load API key from .env file to keep it off Git
load_dotenv() 

# Init client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def encode_image(image_path):
    """Simple base64 encoder."""
    if not os.path.exists(image_path):
        return None
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_mask_map(mask_path):
    """
    Pre-index mask files into a dictionary. 
    Much faster than os.listdir() inside the loop.
    """
    if not mask_path or not os.path.exists(mask_path):
        return {}
    
    mask_map = {}
    for f in os.listdir(mask_path):
        # Assuming filename structure: ID_Number_Type.png
        parts = f.split('_')
        if len(parts) > 1:
            key = parts[1] # This matches the image ID logic
            if key not in mask_map:
                mask_map[key] = []
            mask_map[key].append(f)
    return mask_map

async def generate_conversations(image_list, prompt=None, desc=None, mask_path=None, save_path="result.csv", prefix_name=None, ext=""):
    
    # 1. Pre-load masks for speed
    mask_map = get_mask_map(mask_path)
    
    # 2. Limit concurrency to avoid hitting API rate limits (e.g., 10 requests at a time)
    sem = asyncio.Semaphore(10)

    # Dictionary for mask type mapping
    mask_type_map = {
        "EX": "Hard Exudates mask",
        "HE": "Haemorrhages mask",
        "MA": "Microaneurysms mask",
        "SE": "Soft Exudates mask"
    }

    async def process_image(image_path):
        async with sem: # distinct from gather, controls active requests
            try:
                # Extract ID from filename
                img_name = os.path.basename(image_path)
                img_id_part = img_name.split('.')[0].split('_')[1]
                
                # Get text description
                img_desc = ""
                if desc:
                    img_desc = desc.get_description(image_path)
                img_desc += ext
                if img_desc: 
                    img_desc += ","

                # Handle masks
                img_mask_payloads = []
                related_masks = mask_map.get(img_id_part, [])
                
                for m_file in related_masks:
                    # Append mask descriptions
                    m_parts = m_file.split('.')[0].split('_')
                    if len(m_parts) > 2:
                        m_type = m_parts[2]
                        if m_type in mask_type_map:
                            img_desc += f"{mask_type_map[m_type]},"
                    
                    # Encode mask image
                    full_mask_path = os.path.join(mask_path, m_file)
                    b64_mask = encode_image(full_mask_path)
                    if b64_mask:
                        img_mask_payloads.append({
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{b64_mask}"}
                        })

                # Formatting
                img_desc = img_desc.rstrip(",")
                
                # Construct Message
                user_content = [{"type": "text", "text": img_desc}]
                if img_mask_payloads:
                    user_content.extend(img_mask_payloads)

                messages = [
                    {"role": "system", "content": prompt()},
                    {"role": "user", "content": user_content}
                ]

                # Call API
                response = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages
                )
                
                res_content = response.choices[0].message.content
                return {"id": img_name.split('.')[0], "boundingbox": res_content}

            except Exception as e:
                print(f"Error processing {image_path}: {e}")
                return None

    async def append_to_csv(data):
        # Use csv module with StringIO to handle special characters/commas safely
        output = io.StringIO()
        writer = csv.writer(output)
        
        # If file is new, write header
        if not os.path.exists(save_path):
             writer.writerow(["id", "boundingbox"])

        # Format the row
        row = [f"{data['id']}.png", json.dumps(data["boundingbox"], ensure_ascii=False)]
        writer.writerow(row)
        
        async with aiofiles.open(save_path, "a", encoding="utf-8") as f:
            await f.write(output.getvalue())

    # --- Execution Flow ---
    
    tasks = [process_image(img) for img in image_list]
    
    # Use as_completed to save results as they finish (better for long jobs)
    for future in asyncio.as_completed(tasks):
        result = await future
        if result:
            await append_to_csv(result)
            print(f"Saved: {result['id']}")

    print("Done.")