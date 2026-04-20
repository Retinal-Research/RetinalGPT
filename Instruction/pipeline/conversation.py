import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Optional

import pandas as pd

from instruction_gen_async import generate_conversations


@dataclass
class ConversationGenerationJob:
    image_list: list
    prompt: Callable[[], str]
    desc: Any
    save_path: str
    prefix_name: str = ""
    ext: str = ""
    image_path: Optional[str] = None
    align: bool = False
    concurrency: int = 10
    model: str = "gpt-4o-mini"


def load_image_list_from_csv(csv_path, filename_col=0, start=0, end=None):
    files = pd.read_csv(csv_path)
    image_list = files.iloc[:, filename_col].tolist()
    if end is None:
        return image_list[start:]
    return image_list[start:end]


def load_image_list_from_dir(images_dir):
    import os

    return os.listdir(images_dir)


async def run_conversation_generation(job: ConversationGenerationJob):
    await generate_conversations(
        image_list=job.image_list,
        prompt=job.prompt,
        desc=job.desc,
        save_path=job.save_path,
        image_path=job.image_path,
        prefix_name=job.prefix_name,
        ext=job.ext,
        concurrency=job.concurrency,
        model=job.model,
        align=job.align,
    )


def run_job_sync(job: ConversationGenerationJob):
    asyncio.run(run_conversation_generation(job))
