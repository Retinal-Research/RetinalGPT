from pipeline_prompts import odir_alignment_prompt, odir_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return odir_instruction_prompt()


def create_prompt_alignment():
    return odir_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("ODIR_instruction_direct")


def run_alignment():
    run_named_pipeline_job("ODIR_alignment_batch")


if __name__ == "__main__":
    run_instruction()
