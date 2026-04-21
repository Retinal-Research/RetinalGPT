import argparse
import asyncio
import importlib
import json
import os
import time

import pandas as pd

from convert2json import convert_file_to_nested_format
from instruction_gen_async import generate_conversations
from pipeline_prompts import PROMPT_REGISTRY
from utils import create_batch


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "configs", "pipeline_jobs.json")


def load_jobs(config_path=CONFIG_PATH):
    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_job(job_name, config_path=CONFIG_PATH):
    jobs = load_jobs(config_path)
    if job_name not in jobs:
        raise KeyError(f"Unknown pipeline job: {job_name}")
    return jobs[job_name]


def build_image_list(image_list_config):
    image_list_type = image_list_config["type"]

    if image_list_type == "dir":
        image_list = os.listdir(image_list_config["path"])
    elif image_list_type == "csv_column":
        files = pd.read_csv(image_list_config["path"])
        image_list = files.iloc[:, image_list_config.get("column", 0)].tolist()
    elif image_list_type == "explicit":
        image_list = image_list_config["values"]
    else:
        raise ValueError(f"Unsupported image list type: {image_list_type}")

    start = image_list_config.get("start")
    end = image_list_config.get("end")
    if start is not None or end is not None:
        image_list = image_list[start:end]

    return image_list


def build_desc(desc_config):
    module = importlib.import_module(desc_config["module"])
    desc_class = getattr(module, desc_config["class"])
    return desc_class(**desc_config.get("kwargs", {}))


def build_prompt(prompt_name):
    if prompt_name not in PROMPT_REGISTRY:
        raise KeyError(f"Unknown pipeline prompt: {prompt_name}")
    return PROMPT_REGISTRY[prompt_name]


async def run_direct_generate(job_config):
    image_list = build_image_list(job_config["image_list"])
    desc = build_desc(job_config["desc"])
    prompt = build_prompt(job_config["prompt"])

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
        type=job_config.get("type")
    )

    if "instruction_save" in job_config:
        convert_file_to_nested_format(job_config["save_path"], job_config["instruction_save"])


async def run_direct_generate_batched(job_config):
    image_list = build_image_list(job_config["image_list"])
    desc = build_desc(job_config["desc"])
    prompt = build_prompt(job_config["prompt"])

    batch_size = job_config.get("batch_size", 50)
    max_retries = job_config.get("max_retries", 3)
    sleep_seconds = job_config.get("sleep_seconds", 3)

    async def process_batch(start, end):
        for attempt in range(max_retries):
            try:
                print(f"Processing batch {start} to {end}, Attempt {attempt + 1}...")
                await generate_conversations(
                    image_list=image_list[start:end],
                    prompt=prompt,
                    desc=desc,
                    save_path=job_config["save_path"],
                    image_path=job_config.get("image_path"),
                    prefix_name=job_config.get("prefix_name", ""),
                    ext=job_config.get("ext", ""),
                    concurrency=job_config.get("concurrency", 10),
                    model=job_config.get("model", "gpt-4o-mini"),
                    type=job_config.get("type")
                )
                print(f"Batch {start} to {end} completed successfully.")
                return
            except Exception as error:
                print(f"Error processing batch {start} to {end}: {error}")
                if attempt < max_retries - 1:
                    print("Retrying after 10 seconds...")
                    await asyncio.sleep(10)
                else:
                    print("Max retries reached. Skipping this batch.")

    for idx in range(0, len(image_list), batch_size):
        await process_batch(idx, min(idx + batch_size, len(image_list)))
        print(f"Sleeping for {sleep_seconds} seconds before the next batch...")
        await asyncio.sleep(sleep_seconds)

    if "instruction_save" in job_config:
        convert_file_to_nested_format(job_config["save_path"], job_config["instruction_save"])


def run_batch_create(job_config):
    image_list = build_image_list(job_config["image_list"])
    desc = build_desc(job_config["desc"])
    prompt = build_prompt(job_config["prompt"])

    create_batch(
        image_list=image_list,
        desc=desc,
        prompt=prompt,
        img_path=job_config.get("img_path"),
        save_path=job_config["save_path"],
        ext=job_config.get("ext", "")
    )


def run_named_pipeline_job(job_name, config_path=CONFIG_PATH):
    job_config = load_job(job_name, config_path=config_path)
    action = job_config["action"]

    if action == "direct_generate":
        asyncio.run(run_direct_generate(job_config))
        return

    if action == "direct_generate_batched":
        asyncio.run(run_direct_generate_batched(job_config))
        return

    if action == "batch_create":
        run_batch_create(job_config)
        return

    raise ValueError(f"Unsupported pipeline action: {action}")


def main():
    parser = argparse.ArgumentParser(description="Run config-driven pipeline jobs.")
    parser.add_argument("job_name", type=str, help="Job name defined in configs/pipeline_jobs.json")
    args = parser.parse_args()
    run_named_pipeline_job(args.job_name)


if __name__ == "__main__":
    main()
