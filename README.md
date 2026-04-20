# RetinalGPT

RetinalGPT is a retinal multimodal assistant built on large vision-language models.

This repository contains the **data construction pipeline** used to build retinal instruction-following conversations for the paper:

- [RetinalGPT: A Retinal Clinical Preference Conversational Assistant Powered by Large Vision-Language Models](https://arxiv.org/pdf/2503.03987)
- [Hugging Face Model](https://huggingface.co/ASU-GSL/RetinalGPT)

## Overview

The main workflow in this repo is:

1. Build dataset-specific retinal descriptions through `Desc` classes.
2. Combine structured signals such as disease labels, image quality, fractal features, and lesion annotations.
3. Send the composed context to the API to generate multi-turn conversations.
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
│   ├── pipeline/                     # Structured pipeline wrapper
│   ├── run_conversation_pipeline.py  # Unified entrypoint
│   ├── instruction_gen_async.py      # API-based conversation generation
│   ├── convert2json.py               # Output parsing / JSON conversion
│   ├── utils.py                      # Batch helpers and post-processing
│   ├── ins_*.py                      # Dataset-specific generation scripts
│   └── batch_file_*.py               # Batch request generation scripts
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

### 2. Conversation Generation

The main generation logic lives in:

- `Instruction/instruction_gen_async.py`

This module supports:

- async API calls
- text-only generation
- image-conditioned generation
- compatibility with older script-style calls already present in this repo

### 3. Structured Pipeline Entry

For a cleaner workflow, the recommended entrypoint is:

- `Instruction/run_conversation_pipeline.py`

This wrapper lets you specify:

- image list source
- prompt module and function
- description class
- description kwargs
- output path
- optional image root

without rewriting a new script for each run.

## Quick Start

### Run the unified pipeline

```bash
cd Instruction

python3 run_conversation_pipeline.py \
  --images-csv Results_VD/M4/macula_features.csv \
  --save-path batch_simple/instruction/jsonl/UK.jsonl \
  --prefix-name UK/ \
  --ext ",this image has vascular dementia, the modality of the image is Color Fundus Photograph" \
  --prompt-module ins_UK \
  --prompt-func create_prompt \
  --desc-module Desc.UKDesc \
  --desc-class UKDesc \
  --desc-kwargs-json '{"fractal_analysis_csv":"frac_analysis/csv_sig/UK_VD.csv","quality_csv":"Results_VD/M1/results_ensemble.csv"}'
```

### Output

The pipeline writes conversation samples into JSONL files with fields such as:

- `id`
- `image`
- `conversations`

These outputs can then be merged, cleaned, aligned, or converted into nested JSON using the helper scripts already included in `Instruction/`.

## Working Pattern

The codebase currently supports two usage patterns:

### Script-first pattern

Use the existing dataset scripts such as:

- `Instruction/ins_UK.py`
- `Instruction/ins_IDRID.py`
- `Instruction/ins_RFMiD.py`

This matches the original experimental workflow.

### Pipeline-first pattern

Use `Instruction/run_conversation_pipeline.py` with modular arguments.

This is the cleaner option if you want a more maintainable way to run the same desc -> API -> conversation flow across datasets.

## Notes

- This repository is intended for **research and data construction**.
- It is centered on retinal conversation generation and instruction data preparation.
- Some dataset scripts still preserve the original experiment-style organization for reproducibility.
- The `figures/` directory stores paper-related assets, but the README intentionally keeps the presentation lightweight.

## Citation

If you find this project useful, please cite the paper linked above.

## Acknowledgement

We thank the LLaVA and LLaVA-Med projects, especially the legacy `v0` line, for the foundational environment and open-source vision-language modeling framework that supported this work.
