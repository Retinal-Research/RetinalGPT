from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
import sys

import pandas as pd

INSTRUCTION_ROOT = Path(__file__).resolve().parents[1]
if str(INSTRUCTION_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUCTION_ROOT))

from instruction_gen_async import generate_conversations
from sample.instruction_prompt import sample_instruction_prompt
from sample.user_dataset_desc import UserDatasetDescription


def load_image_list(metadata_csv: str, image_column: str) -> list[str]:
    data = pd.read_csv(metadata_csv)
    if image_column not in data.columns:
        raise ValueError(f"Missing required image column: {image_column}")
    return data[image_column].dropna().astype(str).tolist()


async def run(args):
    image_list = load_image_list(args.metadata_csv, args.image_column)
    desc = UserDatasetDescription(args.metadata_csv, image_column=args.image_column)

    await generate_conversations(
        image_list=image_list,
        prompt=sample_instruction_prompt,
        desc=desc,
        save_path=args.output_jsonl,
        image_path=args.image_dir,
        prefix_name=args.image_prefix,
        ext=args.extra_suffix,
        concurrency=args.concurrency,
        model=args.model,
    )


def main():
    parser = argparse.ArgumentParser(description="Sample runner for generating instruction conversations from custom retinal data.")
    parser.add_argument("--metadata-csv", default="sample/metadata_template.csv", help="CSV with one row per image.")
    parser.add_argument("--image-dir", default="/path/to/your/images", help="Directory containing your retinal images.")
    parser.add_argument("--output-jsonl", default="sample/generated_instruction_conversations.jsonl", help="Where to save the generated conversations.")
    parser.add_argument("--image-column", default="image", help="Column name containing image file names.")
    parser.add_argument("--image-prefix", default="", help="Optional prefix written into the output image field.")
    parser.add_argument("--extra-suffix", default="", help="Optional extra text appended to each hidden description.")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrent API requests.")
    parser.add_argument("--model", default="gpt-4o-mini", help="Model name used for generation.")
    args = parser.parse_args()
    if not os.path.exists(args.metadata_csv):
        raise FileNotFoundError(f"Metadata CSV not found: {args.metadata_csv}")
    if args.image_dir == "/path/to/your/images":
        raise ValueError("Please set --image-dir to your real image directory.")
    if not os.path.isdir(args.image_dir):
        raise NotADirectoryError(f"Image directory not found: {args.image_dir}")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
