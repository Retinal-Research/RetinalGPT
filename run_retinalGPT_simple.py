import argparse
import os

import torch
from PIL import Image
from transformers import AutoConfig, AutoTokenizer, CLIPImageProcessor, CLIPVisionModel

from llava import LlavaLlamaForCausalLM
from llava.conversation import conv_templates
from llava.utils import disable_torch_init


DEFAULT_IMAGE_PATCH_TOKEN = "<im_patch>"
DEFAULT_IM_START_TOKEN = "<im_start>"
DEFAULT_IM_END_TOKEN = "<im_end>"


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


def build_query(question, image_token_len, mm_use_im_start_end):
    question = question.strip()
    if mm_use_im_start_end:
        return question + "\n" + DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_PATCH_TOKEN * image_token_len + DEFAULT_IM_END_TOKEN
    return question + "\n" + DEFAULT_IMAGE_PATCH_TOKEN * image_token_len


def eval_model(args):
    disable_torch_init()
    model_name = os.path.expanduser(args.model_name)
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

    image = Image.open(os.path.expanduser(args.image_file)).convert("RGB")
    image_tensor = image_processor.preprocess(image, return_tensors="pt")["pixel_values"][0].unsqueeze(0).half().cuda()

    conv = conv_templates[args.conv_mode].copy()
    qs = build_query(args.question, image_token_len, mm_use_im_start_end)
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
    print(outputs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", type=str, required=True, help="RetinalGPT or LLaVA model path")
    parser.add_argument("--image-file", type=str, required=True, help="Input image path")
    parser.add_argument("--question", type=str, required=True, help="Input question")
    parser.add_argument("--mm-projector", type=str, default=None)
    parser.add_argument("--vision-tower", type=str, default=None)
    parser.add_argument("--conv-mode", type=str, default="simple")
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--max-new-tokens", type=int, default=256)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        raise EnvironmentError("CUDA is required to run RetinalGPT inference with this script.")
    if not os.path.exists(os.path.expanduser(args.image_file)):
        raise FileNotFoundError(f"Image file not found: {args.image_file}")
    if args.mm_projector is not None and args.vision_tower is None:
        raise ValueError("--vision-tower is required when --mm-projector is provided.")

    eval_model(args)
