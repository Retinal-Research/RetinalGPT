from pipeline_prompts import miccai_task2_alignment_prompt, miccai_task2_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return miccai_task2_instruction_prompt()


def create_prompt_alignment():
    return miccai_task2_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("MICCAI_task2_instruction_direct")


def run_alignment():
    run_named_pipeline_job("MICCAI_task2_alignment_batch")


if __name__ == "__main__":
    run_instruction()
