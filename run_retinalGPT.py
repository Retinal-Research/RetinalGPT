import argparse
import json
import os

import shortuuid
import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoConfig, AutoTokenizer, CLIPImageProcessor, CLIPVisionModel

from llava import LlavaLlamaForCausalLM
from llava.conversation import conv_templates
from llava.utils import disable_torch_init


DEFAULT_IMAGE_PATCH_TOKEN = "<im_patch>"
DEFAULT_IM_START_TOKEN = "<im_start>"
DEFAULT_IM_END_TOKEN = "<im_end>"
DEFAULT_QUERY = "Please describe this retinal image in detail."


def patch_config(config):
    patch_dict = {
        "use_mm_proj": True,
        "mm_vision_tower": "openai/clip-vit-large-patch14",
        "mm_hidden_size": 1024,
    }

    cfg = AutoConfig.from_pretrained(config)
    if not hasattr(cfg, "mm_vision_tower"):
        print(f"`mm_vision_tower` not found in `{config}`, applying patch and save to disk.")
        for key, value in patch_dict.items():
            setattr(cfg, key, value)
        cfg.save_pretrained(config)


def load_questions(entry, default_query):
    if "questions" in entry and isinstance(entry["questions"], list):
        questions = [str(question).strip() for question in entry["questions"] if str(question).strip()]
        if questions:
            return questions

    if "question" in entry and str(entry["question"]).strip():
        return [str(entry["question"]).strip()]

    conversations = entry.get("messages", [])
    questions = []
    for conv in conversations:
        role = conv.get("from") or conv.get("role")
        if role in {"human", "user"}:
            value = conv.get("value") or conv.get("content", "")
            value = str(value).replace("<image>", "").strip()
            if value:
                questions.append(value)

    if questions:
        return questions

    return [default_query]


def build_prompt(question, image_token_len, mm_use_im_start_end):
    question = question.strip()
    if mm_use_im_start_end:
        return question + "\n" + DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_PATCH_TOKEN * image_token_len + DEFAULT_IM_END_TOKEN
    return question + "\n" + DEFAULT_IMAGE_PATCH_TOKEN * image_token_len


def clean_outputs(outputs, conv_mode, conv_sep):
    if conv_mode == "simple_legacy" or conv_mode == "simple":
        while True:
            cur_len = len(outputs)
            outputs = outputs.strip()
            for pattern in ["###", "Assistant:", "Response:"]:
                if outputs.startswith(pattern):
                    outputs = outputs[len(pattern):].strip()
            if len(outputs) == cur_len:
                break

    try:
        index = outputs.index(conv_sep)
    except ValueError:
        outputs += conv_sep
        index = outputs.index(conv_sep)

    return outputs[:index].strip()


def load_question_file(question_file):
    question_file = os.path.expanduser(question_file)
    if not os.path.exists(question_file):
        raise FileNotFoundError(f"Question file not found: {question_file}")
    if question_file.endswith(".jsonl"):
        data = []
        with open(question_file, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    data.append(json.loads(line))
        return data

    with open(question_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return data["data"]
        return [data]
    return data


def split_list(data, num_chunks, chunk_idx):
    if num_chunks <= 1:
        return data

    if chunk_idx < 0 or chunk_idx >= num_chunks:
        raise ValueError(f"chunk_idx must be in [0, {num_chunks - 1}], but got {chunk_idx}")

    chunk_size = (len(data) + num_chunks - 1) // num_chunks
    start = chunk_idx * chunk_size
    end = min(start + chunk_size, len(data))
    return data[start:end]


def ensure_output_path(path):
    path = os.path.expanduser(path)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    return path


def eval_model(args):
    disable_torch_init()
    model_name = os.path.expanduser(args.model_name)
    image_folder = os.path.expanduser(args.image_folder)
    if not os.path.isdir(image_folder):
        raise FileNotFoundError(f"Image folder not found: {image_folder}")
    if args.conv_mode not in conv_templates:
        raise ValueError(f"Unknown conv mode: {args.conv_mode}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if args.mm_projector is None:
        patch_config(model_name)
        model = LlavaLlamaForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).cuda()
        image_processor = CLIPImageProcessor.from_pretrained(model.config.mm_vision_tower, torch_dtype=torch.float16)

        mm_use_im_start_end = getattr(model.config, "mm_use_im_start_end", False)
        tokenizer.add_tokens([DEFAULT_IMAGE_PATCH_TOKEN], special_tokens=True)
        if mm_use_im_start_end:
            tokenizer.add_tokens([DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN], special_tokens=True)

        vision_tower = model.model.vision_tower[0]
        vision_tower.to(device="cuda", dtype=torch.float16)
        vision_config = vision_tower.config
        vision_config.im_patch_token = tokenizer.convert_tokens_to_ids([DEFAULT_IMAGE_PATCH_TOKEN])[0]
        vision_config.use_im_start_end = mm_use_im_start_end
        if mm_use_im_start_end:
            vision_config.im_start_token, vision_config.im_end_token = tokenizer.convert_tokens_to_ids(
                [DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN]
            )
        image_token_len = (vision_config.image_size // vision_config.patch_size) ** 2
    else:
        model = LlavaLlamaForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16).cuda()
        vision_tower = CLIPVisionModel.from_pretrained(args.vision_tower, torch_dtype=torch.float16).cuda()
        image_processor = CLIPImageProcessor.from_pretrained(args.vision_tower, torch_dtype=torch.float16)

        mm_use_im_start_end = getattr(model.config, "mm_use_im_start_end", False)
        tokenizer.add_tokens([DEFAULT_IMAGE_PATCH_TOKEN], special_tokens=True)
        if mm_use_im_start_end:
            tokenizer.add_tokens([DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN], special_tokens=True)

        vision_config = vision_tower.config
        vision_config.im_patch_token = tokenizer.convert_tokens_to_ids([DEFAULT_IMAGE_PATCH_TOKEN])[0]
        vision_config.use_im_start_end = mm_use_im_start_end
        if mm_use_im_start_end:
            vision_config.im_start_token, vision_config.im_end_token = tokenizer.convert_tokens_to_ids(
                [DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN]
            )

        image_token_len = (vision_config.image_size // vision_config.patch_size) ** 2

        mm_projector = torch.nn.Linear(vision_config.hidden_size, model.config.hidden_size)
        mm_projector_weights = torch.load(args.mm_projector, map_location="cpu")
        mm_projector.load_state_dict({key.split(".")[-1]: value for key, value in mm_projector_weights.items()})

        model.model.mm_projector = mm_projector.cuda().half()
        model.model.vision_tower = [vision_tower]

    model.eval()
    data = load_question_file(args.question_file)
    data = split_list(data, args.num_chunks, args.chunk_idx)
    answers_file = ensure_output_path(args.answers_file)
    file_mode = "a" if args.append else "w"

    with open(answers_file, file_mode, encoding="utf-8") as file:
        for entry in tqdm(data, desc="Processing images"):
            image_file = entry.get("image") or entry.get("images")
            if image_file is None:
                raise ValueError("Each input item must contain `image` or `images`.")

            questions = load_questions(entry, args.default_query)
            if args.max_questions > 0:
                questions = questions[:args.max_questions]

            image_path = os.path.join(image_folder, image_file)
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")

            image = Image.open(image_path).convert("RGB")
            image_tensor = image_processor.preprocess(image, return_tensors="pt")["pixel_values"][0].unsqueeze(0).half().cuda()
            answers = []

            conv = conv_templates[args.conv_mode].copy()
            first_question = True
            for question in questions:
                if first_question:
                    first_question = False
                    qs = build_prompt(question, image_token_len, mm_use_im_start_end)
                else:
                    qs = question.strip()

                conv.append_message(conv.roles[0], qs)
                prompt = conv.get_prompt()
                inputs = tokenizer([prompt], return_tensors="pt").input_ids.cuda()

                with torch.inference_mode():
                    output_ids = model.generate(
                        inputs,
                        images=image_tensor,
                        do_sample=args.temperature > 0,
                        temperature=args.temperature,
                        max_new_tokens=args.max_new_tokens,
                    )

                input_token_len = inputs.shape[1]
                outputs = tokenizer.batch_decode(output_ids[:, input_token_len:], skip_special_tokens=True)[0]
                outputs = clean_outputs(outputs, args.conv_mode, conv.sep)
                conv.append_message(conv.roles[1], outputs)
                answers.append({"question": question, "answer": outputs})

                if args.verbose:
                    print(question)
                    print(outputs)

            result_id = entry.get("id")
            if not result_id:
                result_id = shortuuid.uuid()

            file.write(
                json.dumps(
                    {"id": result_id, "image": image_file, "qa_pairs": answers},
                    ensure_ascii=False,
                )
                + "\n"
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, required=True, help="RetinalGPT or LLaVA model path")
    parser.add_argument("--image-folder", type=str, required=True, help="Folder containing input images")
    parser.add_argument("--question-file", type=str, required=True, help="Input JSON or JSONL file")
    parser.add_argument("--answers-file", type=str, required=True, help="Output JSONL file")
    parser.add_argument("--mm-projector", type=str, default=None)
    parser.add_argument("--vision-tower", type=str, default=None)
    parser.add_argument("--conv-mode", type=str, default="simple")
    parser.add_argument("--num-chunks", type=int, default=1)
    parser.add_argument("--chunk-idx", type=int, default=0)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--max-new-tokens", type=int, default=128)
    parser.add_argument("--max-questions", type=int, default=1, help="How many extracted questions to answer per image. Use -1 for all.")
    parser.add_argument("--default-query", type=str, default=DEFAULT_QUERY, help="Fallback question when the input item does not contain any question.")
    parser.add_argument("--append", action="store_true", help="Append to the output file instead of overwriting it.")
    parser.add_argument("--verbose", action="store_true", help="Print question and answer pairs during inference.")
    args = parser.parse_args()

    if args.mm_projector is not None and args.vision_tower is None:
        raise ValueError("--vision-tower is required when --mm-projector is provided.")
    if not torch.cuda.is_available():
        raise EnvironmentError("CUDA is required to run RetinalGPT inference with this script.")

    eval_model(args)
