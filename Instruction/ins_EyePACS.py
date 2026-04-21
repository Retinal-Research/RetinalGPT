from pipeline_prompts import eyepacs_alignment_prompt, eyepacs_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return eyepacs_instruction_prompt()


def create_prompt_alignment():
    return eyepacs_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("EyePACS_instruction_direct")


def run_alignment():
    run_named_pipeline_job("EyePACS_alignment_batch")


if __name__ == "__main__":
    run_instruction()
