from pipeline_prompts import rfmid_alignment_prompt, rfmid_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return rfmid_instruction_prompt()


def create_prompt_alignment():
    return rfmid_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("RFMiD_instruction_batch")


def run_alignment():
    run_named_pipeline_job("RFMiD_alignment_batch")


if __name__ == "__main__":
    run_instruction()
