from pipeline_prompts import idrid_seg_alignment_prompt, idrid_seg_instruction_prompt
from pipeline_runner import run_named_pipeline_job


def create_prompt():
    return idrid_seg_instruction_prompt()


def create_prompt_alignment():
    return idrid_seg_alignment_prompt()


def run_instruction():
    run_named_pipeline_job("IDRID_seg_instruction_direct")


def run_alignment():
    run_named_pipeline_job("IDRID_seg_alignment_batch")


if __name__ == "__main__":
    run_instruction()
