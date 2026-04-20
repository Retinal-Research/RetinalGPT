import asyncio
import aiofiles
import json
import base64
import os
import io
import csv
from openai import AsyncOpenAI
from dotenv import load_dotenv
from convert2json import convert_to_map  # Ensure this matches your local file


class RetinalDataPipeline:
    def __init__(self, concurrency=10):
        # Load env vars
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables.")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.sem = asyncio.Semaphore(concurrency) # Shared concurrency limit
        self.model = "gpt-4o-mini"

    def _encode_image(self, image_path):
        """Helper: Base64 encoder."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding {image_path}: {e}")
            return None

    def _index_masks(self, mask_path):
        """Helper: Pre-index mask files for O(1) lookup."""
        mask_map = {}
        if not mask_path or not os.path.exists(mask_path):
            return mask_map
            
        print("Indexing masks...")
        for f in os.listdir(mask_path):
            # Assumes format: ID_Number_Type.png
            parts = f.split('_')
            if len(parts) > 1:
                key = parts[1] 
                if key not in mask_map:
                    mask_map[key] = []
                mask_map[key].append(f)
        return mask_map

    async def _write_csv(self, file_path, row, header=None):
        """Helper: Safe CSV writer."""
        is_new = not os.path.exists(file_path)
        output = io.StringIO()
        writer = csv.writer(output)
        
        if is_new and header:
            writer.writerow(header)
        writer.writerow(row)
        
        async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
            await f.write(output.getvalue())

    async def _write_jsonl(self, file_path, data):
        """Helper: Append JSON line."""
        async with aiofiles.open(file_path, "a", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False) + "\n")

    # ==========================================
    # Task A: Mask Based Bounding Box Generation
    # ==========================================
    async def run_mask_task(self, image_list, prompt_func, desc_obj, mask_path, save_path="bbox_output.csv", ext=""):
        """
        Generates bounding boxes based on mask images.
        Output: CSV file.
        """
        mask_map = self._index_masks(mask_path)
        
        mask_types = {
            "EX": "Hard Exudates mask", "HE": "Haemorrhages mask",
            "MA": "Microaneurysms mask", "SE": "Soft Exudates mask"
        }

        async def _worker(img_name):
            async with self.sem:
                try:
                    # Extract ID (ID_Number format)
                    img_id = img_name.split('.')[0]
                    id_key = img_id.split('_')[1] if '_' in img_id else img_id

                    # 1. Build Description
                    desc_text = desc_obj.get_description(img_name) if desc_obj else ""
                    desc_text += ext
                    if desc_text: desc_text += ","

                    # 2. Collect Masks
                    mask_payloads = []
                    for m_file in mask_map.get(id_key, []):
                        # Add mask type to description
                        m_parts = m_file.split('.')[0].split('_')
                        if len(m_parts) > 2 and m_parts[2] in mask_types:
                            desc_text += f"{mask_types[m_parts[2]]},"
                        
                        # Encode mask
                        b64 = self._encode_image(os.path.join(mask_path, m_file))
                        if b64:
                            mask_payloads.append({
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{b64}"}
                            })

                    desc_text = desc_text.rstrip(",")
                    
                    # 3. Construct Message
                    content = [{"type": "text", "text": desc_text}]
                    content.extend(mask_payloads)

                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": prompt_func()},
                            {"role": "user", "content": content}
                        ]
                    )
                    
                    res_txt = response.choices[0].message.content
                    return {"id": img_id, "bbox": res_txt}

                except Exception as e:
                    print(f"[Mask Task] Error {img_name}: {e}")
                    return None

        # Execute
        print(f"Starting Mask Task for {len(image_list)} images...")
        tasks = [asyncio.create_task(_worker(img)) for img in image_list]
        
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                # Format specific for Task A
                csv_row = [f"{res['id']}.png", json.dumps(res["bbox"], ensure_ascii=False)]
                await self._write_csv(save_path, csv_row, header=["id", "boundingbox"])
                print(f"Saved Mask Result: {res['id']}")

    # ==========================================
    # Task B: Conversation Generation
    # ==========================================
    async def run_conversation_task(self, image_list, prompt_func, desc_obj, image_dir=None, save_path="conv_output.jsonl", prefix="", ext="", align=False):
        """
        Generates conversations based on raw images and/or text.
        Output: JSONL file.
        """
        async def _worker(img_name):
            async with self.sem:
                try:
                    # 1. Prepare Text
                    desc_text = desc_obj.get_description(img_name) if desc_obj else ""
                    desc_text += ext
                    
                    if not desc_text and not image_dir:
                        return None # Nothing to send

                    # 2. Build Message
                    messages = []
                    if image_dir:
                        # Multimodal mode
                        b64 = self._encode_image(os.path.join(image_dir, img_name))
                        if not b64: return None
                        
                        messages = [
                            {"role": "system", "content": prompt_func()},
                            {"role": "user", "content": [
                                {"type": "text", "text": desc_text},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                            ]}
                        ]
                    else:
                        # Text-only mode
                        messages = [
                            {"role": "system", "content": prompt_func()},
                            {"role": "user", "content": desc_text}
                        ]

                    # 3. API Call
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        timeout=60
                    )
                    
                    raw_res = response.choices[0].message.content
                    data_map = convert_to_map(raw_res, align=align)
                    
                    return {
                        "id": img_name.split('.')[0],
                        "image": f"{prefix}{img_name}",
                        "conversations": data_map
                    }

                except Exception as e:
                    print(f"[Conv Task] Error {img_name}: {e}")
                    return None

        # Execute
        print(f"Starting Conversation Task for {len(image_list)} images...")
        tasks = [asyncio.create_task(_worker(img)) for img in image_list]
        
        for future in asyncio.as_completed(tasks):
            res = await future
            if res:
                await self._write_jsonl(save_path, res)
                print(f"Saved Conversation: {res['id']}")


async def generate_conversations(
    image_list,
    prompt=None,
    desc=None,
    save_path="conversations.jsonl",
    image_path=None,
    prefix_name="",
    ext="",
    concurrency=10,
    model="gpt-4o-mini",
    type=None,
    **kwargs
):
    """
    Backward-compatible entrypoint used by existing scripts in this repo.
    This keeps the old call style while routing to RetinalDataPipeline.
    """
    image_dir = kwargs.pop("image_dir", None) or image_path
    prefix = kwargs.pop("prefix", None) or prefix_name

    align = kwargs.pop("align", None)
    if align is None:
        align = (type == "align")

    pipeline = RetinalDataPipeline(concurrency=concurrency)
    pipeline.model = model

    await pipeline.run_conversation_task(
        image_list=image_list,
        prompt_func=prompt,
        desc_obj=desc,
        image_dir=image_dir,
        save_path=save_path,
        prefix=prefix,
        ext=ext,
        align=align
    )

# Example Usage (can be in main.py)
if __name__ == "__main__":
    # Mock objects for testing
    class MockDesc:
        def get_description(self, name): return "Patient with mild DR."
    
    pipeline = RetinalDataPipeline(concurrency=5)
    
    # Run Mask Task
    # asyncio.run(pipeline.run_mask_task(
    #     image_list=["img_1.png"], 
    #     prompt_func=lambda: "Find lesions.", 
    #     desc_obj=MockDesc(), 
    #     mask_path="./masks
    # ))

    # Run Conversation Task
    # asyncio.run(pipeline.run_conversation_task(
    #     image_list=["img_1.png"], 
    #     prompt_func=lambda: "Create Q&A.", 
    #     desc_obj=MockDesc(),
    #     image_dir="./images"
    # ))
