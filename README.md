# RetinalGPT

RetinalGPT is a retinal multimodal assistant built on large vision-language models.

This repository contains the **data construction pipeline** used to build retinal instruction-following conversations for the paper:

- [RetinalGPT: A Retinal Clinical Preference Conversational Assistant Powered by Large Vision-Language Models](https://arxiv.org/pdf/2503.03987)
- [Hugging Face Model](https://huggingface.co/ASU-GSL/RetinalGPT)

## Overview

The main workflow in this repo is:

1. Build dataset-specific retinal descriptions through `Desc` classes.
2. Construct two types of data:
   - `instruction`
   - `alignment`
3. Run the pipeline in one of two modes:
   - `direct` generation
   - `batch` request packaging / unpacking
4. Convert generated outputs into instruction-tuning JSONL / JSON files.

This repo is **not** the full end-to-end training codebase for the entire project. It focuses on the retinal data processing and conversation generation pipeline.

## Environment

The environment follows the **LLaVA base setup used for legacy `v0` workflows** in our project.

In practice, we use the standard LLaVA-style base environment and then install the extra packages needed by this repository:

```bash
conda create -n retinalgpt python=3.10 -y
conda activate retinalgpt
pip install --upgrade pip
pip install -r requirements.txt
```

If you already have a working LLaVA / `llava-v0` style environment, you can usually reuse it directly. For more details on the upstream base setup, please refer to the official LLaVA repository.

## Repository Structure

```text
RetinalGPT/
├── Instruction/
│   ├── Desc/                         # Dataset-specific description builders
│   ├── configs/                      # Config-driven dataset jobs
│   ├── tools/                        # Bounding box + postprocess helpers
│   ├── legacy/                       # Old experiment scripts kept for reference
│   ├── pipeline/                     # Shared pipeline helpers
│   ├── pipeline_runner.py            # Config-driven instruction/alignment runner
│   ├── batch_runner.py               # Config-driven batch runner
│   ├── pipeline_prompts.py           # Centralized instruction/alignment prompts
│   ├── batch_prompts.py              # Centralized batch prompts
│   ├── instruction_gen_async.py      # API-based conversation generation
│   ├── convert2json.py               # Output parsing / JSON conversion
│   ├── utils.py                      # Shared helper functions
│   ├── ins_*.py                      # Thin dataset wrappers for main pipeline jobs
│   └── batch_file_*.py               # Thin dataset wrappers for batch jobs
├── figures/                          # Paper assets and reference figures
├── requirements.txt
└── README.md
```

## Core Idea

Each dataset is wrapped by a description class in `Instruction/Desc`. These classes map raw metadata into a unified text description that can be consumed by a large multimodal model.

Typical inputs include:

- image quality predictions
- fractal / vascular quantitative features
- disease labels
- lesion masks or bounding boxes
- dataset-specific metadata

The generated description is then appended with task-specific prompt instructions and sent to the API to produce a retinal conversation sample.

## Main Components

### 1. Description Builders

`Instruction/Desc` contains dataset-specific classes such as:

- `APTOSDesc`
- `EyeQDesc`
- `IDRIDDesc`
- `MICCAIDesc`
- `MessidorDesc`
- `ODIRDDesc`
- `RFMiDDesc`
- `UKDesc`

All of them follow the same design goal: turn heterogeneous dataset annotations into a reusable natural-language description.

### 2. Data Targets

The project maintains two data tracks:

- `instruction`: multi-turn retinal conversations
- `alignment`: compact alignment-style supervision, usually one-turn

### 3. Execution Modes

The project maintains two execution modes:

- `direct`: call the API directly and write conversation outputs
- `batch`: package local requests first, send them to the API server, then unpack returned outputs

### 4. Conversation Generation

The main generation logic lives in:

- `Instruction/instruction_gen_async.py`

This module supports:

- async API calls
- text-only generation
- image-conditioned generation
- compatibility with older script-style calls already present in this repo

### 5. Structured Pipeline Entry

For `instruction` / `alignment` construction, the main entrypoint is:

- `Instruction/pipeline_runner.py`

For local batch request packaging and unpacking, the main entrypoint is:

- `Instruction/batch_runner.py`

Both are config-driven and use dataset jobs defined in `Instruction/configs/`.

## Quick Start

### Run an instruction/alignment job

```bash
cd Instruction

python3 pipeline_runner.py UK_instruction_direct
```

### Run a batch packaging job

```bash
cd Instruction

python3 batch_runner.py APTOS
```

### Output

The pipeline writes conversation samples into JSONL files with fields such as:

- `id`
- `image`
- `conversations`

These outputs can then be merged, cleaned, aligned, or converted into nested JSON using the helper scripts already included in `Instruction/`.

## Typical Flow

The intended engineering flow is now:

1. Build hidden metadata with `Desc/*`
2. Choose a dataset job from `Instruction/configs/`
3. Run either:
   - `pipeline_runner.py` for `instruction` / `alignment`
   - `batch_runner.py` for batch request workflows
4. Use `tools/postprocess` to validate / merge / fix / convert outputs
5. Use `tools/bounding_box` to generate or inspect lesion bounding boxes

The existing `ins_*.py` and `batch_file_*.py` files are still available as thin wrappers if you prefer the old entry style.

## Notes

- This repository is intended for **research and data construction**.
- It is centered on retinal conversation generation and instruction data preparation.
- `Instruction/legacy` keeps older one-off experiment scripts for reference.
- The `figures/` directory stores paper-related assets, but the README intentionally keeps the presentation lightweight.

## Citation

If you find this project useful, please cite the paper linked above.

## Acknowledgement

We thank the LLaVA and LLaVA-Med projects, especially the legacy `v0` line, for the foundational environment and open-source vision-language modeling framework that supported this work.
