# 👁️ RetinalGPT: Advancing Clinical Ophthalmology Through Instruction-Tuned Vision–Language Intelligence

[![Code](https://img.shields.io/badge/GitHub-Code-black)](https://github.com/Retinal-Research/RetinalGPT)
[![Paper](https://img.shields.io/badge/arXiv-2503.03987-b31b1b)](https://arxiv.org/abs/2503.03987)
[![Model](https://img.shields.io/badge/HuggingFace-Model-orange)](https://huggingface.co/ASU-GSL/RetinalGPT)

## News

- April 14, 2026: RetinalGPT was submitted to *Ophthalmology Science* and is currently under review.

RetinalGPT is a retinal vision-language assistant for clinically grounded ophthalmic image understanding and conversation.

This repository includes:

- the released RetinalGPT inference scripts
- the retinal instruction/alignment data construction pipeline
- dataset-specific retinal description builders
- a minimal sample for adapting the pipeline to custom data

<p align="center">
  <img src="./figures/chat.png" alt="RetinalGPT chat example" width="320">
</p>

## Installation

```bash
conda create -n retinalgpt python=3.10 -y
conda activate retinalgpt
pip install --upgrade pip
pip install -r requirements.txt
```

CUDA is required for the provided inference scripts.

## Quick Start

### Single-image inference

```bash
python3 run_retinalGPT_simple.py \
  --model-name ASU-GSL/RetinalGPT \
  --image-file /path/to/retinal_image.png \
  --question "Please describe this retinal image in detail."
```

### Batch inference

```bash
python3 run_retinalGPT.py \
  --model-name ASU-GSL/RetinalGPT \
  --image-folder /path/to/images \
  --question-file /path/to/questions.jsonl \
  --answers-file /path/to/predictions.jsonl
```

Example input: [examples/inference/questions.json](./examples/inference/questions.json)

### Instruction/alignment pipeline

```bash
cd Instruction
python3 pipeline_runner.py UK_instruction_direct
```

### Batch packaging pipeline

```bash
cd Instruction
python3 batch_runner.py APTOS
```

### Custom-data sample

```bash
cd Instruction
python3 sample/generate_instruction_conversations.py \
  --metadata-csv sample/metadata_template.csv \
  --image-dir /path/to/your/images \
  --output-jsonl sample/generated_instruction_conversations.jsonl
```

More details: [Instruction/sample/README.md](./Instruction/sample/README.md)

## Repository Structure

```text
RetinalGPT/
├── Instruction/
│   ├── Desc/                 # Dataset-specific description builders
│   ├── configs/              # Pipeline and batch jobs
│   ├── sample/               # Minimal custom-data example
│   ├── batch_runner.py       # Batch request packaging / unpacking
│   ├── pipeline_runner.py    # Instruction / alignment generation
│   └── convert2json.py       # Output conversion helpers
├── figures/
├── llava/
├── run_retinalGPT.py
├── run_retinalGPT_simple.py
└── README.md
```

## Pipeline Overview

The data pipeline converts retinal metadata into hidden textual descriptions, then uses prompt templates to generate instruction-following retinal conversations.

Supported dataset description builders include:

- `APTOSDesc`
- `EyeQDesc`
- `IDRIDDesc`
- `MICCAIDesc`
- `MessidorDesc`
- `ODIRDDesc`
- `RFMiDDesc`
- `UKDesc`

<p align="center">
  <img src="./figures/data_processing.png" alt="RetinalGPT data processing pipeline" width="760">
</p>

## Acknowledgement

We thank the LLaVA and LLaVA-Med projects for their open-source vision-language modeling framework.

## Citation

```bibtex
@article{zhu2025retinalgpt,
  title={Retinalgpt: A retinal clinical preference conversational assistant powered by large vision-language models},
  author={Zhu, Wenhui and Li, Xin and Chen, Xiwen and Qiu, Peijie and Vasa, Vamsi Krishna and Dong, Xuanzhao and Chen, Yanxi and Lepore, Natasha and Dumitrascu, Oana and Su, Yi and others},
  journal={arXiv preprint arXiv:2503.03987},
  year={2025}
}
```
