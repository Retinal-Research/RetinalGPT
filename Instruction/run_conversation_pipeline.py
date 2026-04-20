import argparse
import asyncio
import importlib
import json

from pipeline.conversation import (
    ConversationGenerationJob,
    load_image_list_from_csv,
    load_image_list_from_dir,
    run_conversation_generation,
)


def _load_object(module_path, object_name):
    module = importlib.import_module(module_path)
    return getattr(module, object_name)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Run conversation generation pipeline (desc -> API -> conversations)."
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--images-csv", type=str, help="CSV containing image file names.")
    src.add_argument("--images-dir", type=str, help="Directory containing image files.")
    parser.add_argument("--filename-col", type=int, default=0, help="CSV filename column index.")
    parser.add_argument("--start", type=int, default=0, help="Slice start index.")
    parser.add_argument("--end", type=int, default=None, help="Slice end index (exclusive).")

    parser.add_argument("--save-path", type=str, required=True, help="Output JSONL path.")
    parser.add_argument("--prefix-name", type=str, default="", help="Image prefix in output.")
    parser.add_argument("--ext", type=str, default="", help="Extra prompt context.")
    parser.add_argument("--image-path", type=str, default=None, help="Image root for multimodal requests.")

    parser.add_argument("--prompt-module", type=str, required=True, help="Prompt module path.")
    parser.add_argument("--prompt-func", type=str, required=True, help="Prompt function name.")
    parser.add_argument("--desc-module", type=str, required=True, help="Desc module path.")
    parser.add_argument("--desc-class", type=str, required=True, help="Desc class name.")
    parser.add_argument(
        "--desc-kwargs-json",
        type=str,
        default="{}",
        help="JSON string for desc class kwargs.",
    )

    parser.add_argument("--align", action="store_true", help="Enable align parsing mode.")
    parser.add_argument("--concurrency", type=int, default=10, help="Async request concurrency.")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model id.")

    return parser.parse_args()


def main():
    args = _parse_args()

    if args.images_csv:
        image_list = load_image_list_from_csv(
            csv_path=args.images_csv,
            filename_col=args.filename_col,
            start=args.start,
            end=args.end,
        )
    else:
        image_list = load_image_list_from_dir(args.images_dir)
        if args.end is None:
            image_list = image_list[args.start:]
        else:
            image_list = image_list[args.start : args.end]

    prompt_func = _load_object(args.prompt_module, args.prompt_func)
    desc_cls = _load_object(args.desc_module, args.desc_class)
    desc_kwargs = json.loads(args.desc_kwargs_json)
    desc = desc_cls(**desc_kwargs)

    job = ConversationGenerationJob(
        image_list=image_list,
        prompt=prompt_func,
        desc=desc,
        save_path=args.save_path,
        prefix_name=args.prefix_name,
        ext=args.ext,
        image_path=args.image_path,
        align=args.align,
        concurrency=args.concurrency,
        model=args.model,
    )
    asyncio.run(run_conversation_generation(job))


if __name__ == "__main__":
    main()
