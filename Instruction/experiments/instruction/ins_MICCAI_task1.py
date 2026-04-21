from pathlib import Path
import sys

INSTRUCTION_ROOT = Path(__file__).resolve().parents[2]
if str(INSTRUCTION_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUCTION_ROOT))

from pipeline_prompts import miccai_task1_alignment_prompt, miccai_task1_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return miccai_task1_instruction_prompt()


def create_prompt_alignment():
    return miccai_task1_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("MICCAI_task1_instruction_batch")


def run_alignment():
    run_named_pipeline_job("MICCAI_task1_alignment_batch")


if __name__ == "__main__":
    run_instruction()
