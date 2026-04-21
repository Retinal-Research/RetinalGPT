import argparse
import asyncio
import importlib
import json
import os

import pandas as pd

from batch_prompts import PROMPT_REGISTRY
from convert2json import convert_file_to_nested_format
from instruction_gen_async import generate_conversations
from utils import ana_outputs, create_batch


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "configs", "batch_jobs.json")


def load_batch_jobs(config_path=CONFIG_PATH):
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_job_config(job_name, config_path=CONFIG_PATH):
    jobs = load_batch_jobs(config_path=config_path)
    if job_name not in jobs:
        raise KeyError(f"Unknown batch job: {job_name}")
    return jobs[job_name]


def build_image_list(image_list_config):
    image_list_type = image_list_config["type"]

    if image_list_type == "explicit":
        return image_list_config["values"]

    if image_list_type == "dir":
        return os.listdir(image_list_config["path"])

    if image_list_type == "csv_column":
        files = pd.read_csv(image_list_config["path"])
        return files.iloc[:, image_list_config.get("column", 0)].tolist()

    if image_list_type == "csv_filter_suffix":
        files = pd.read_csv(image_list_config["path"])
        match_column = image_list_config["match_column"]
        match_value = image_list_config["match_value"]
        output_column = image_list_config.get("output_column", 0)
        suffix = image_list_config.get("suffix", "")
        filtered = files[files.iloc[:, match_column] == match_value].iloc[:, output_column].tolist()
        return [f"{item}{suffix}" for item in filtered]

    raise ValueError(f"Unsupported image list type: {image_list_type}")


def build_desc(desc_config):
    module = importlib.import_module(desc_config["module"])
    desc_class = getattr(module, desc_config["class"])
    return desc_class(**desc_config.get("kwargs", {}))


def get_prompt(prompt_name):
    if prompt_name not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown prompt: {prompt_name}")
    return PROMPT_REGISTRY[prompt_name]


def run_unpack_outputs(job_config):
    ana_outputs(
        input_path=job_config["batch_path"],
        save_path=job_config["save_path"],
        prefix_name=job_config.get("prefix_name", ""),
        align=job_config.get("align", False),
    )
    convert_file_to_nested_format(job_config["save_path"], job_config["instruction_save"])


def run_create_batch(job_config):
    image_list = build_image_list(job_config["image_list"])
    desc = build_desc(job_config["desc"])
    prompt = get_prompt(job_config["prompt"])
    create_batch(
        image_list=image_list,
        desc=desc,
        prompt=prompt,
        img_path=job_config.get("img_path"),
        save_path=job_config["save_path"],
        ext=job_config.get("ext", ""),
    )


async def run_generate_conversations(job_config):
    image_list = build_image_list(job_config["image_list"])
    desc = build_desc(job_config["desc"])
    prompt = get_prompt(job_config["prompt"])
    await generate_conversations(
        image_list=image_list,
        prompt=prompt,
        desc=desc,
        save_path=job_config["save_path"],
        image_path=job_config.get("image_path"),
        prefix_name=job_config.get("prefix_name", ""),
        ext=job_config.get("ext", ""),
        concurrency=job_config.get("concurrency", 10),
        model=job_config.get("model", "gpt-4o-mini"),
        type=job_config.get("type"),
    )


def run_named_batch_job(job_name, config_path=CONFIG_PATH):
    job_config = load_job_config(job_name, config_path=config_path)
    action = job_config["action"]

    if action == "create_batch":
        run_create_batch(job_config)
        return

    if action == "unpack_outputs":
        run_unpack_outputs(job_config)
        return

    if action == "generate_conversations":
        asyncio.run(run_generate_conversations(job_config))
        return

    raise ValueError(f"Unsupported batch action: {action}")


def main():
    parser = argparse.ArgumentParser(description="Run config-driven batch jobs.")
    parser.add_argument("job_name", type=str, help="Job name defined in configs/batch_jobs.json")
    args = parser.parse_args()
    run_named_batch_job(args.job_name)


if __name__ == "__main__":
    main()
