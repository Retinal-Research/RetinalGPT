from pipeline_prompts import aptos_alignment_prompt, aptos_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return aptos_instruction_prompt()


def create_prompt_alignment():
    return aptos_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("APTOS_instruction_batch")


def run_alignment():
    run_named_pipeline_job("APTOS_alignment_batch")


if __name__ == "__main__":
    run_instruction()
