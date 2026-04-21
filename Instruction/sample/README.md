# Custom Data Sample

This folder shows the minimal path for using your own retinal data with the RetinalGPT instruction-conversation pipeline.

## Files

- `metadata_template.csv`: template metadata file
- `user_dataset_desc.py`: turns one metadata row into the hidden description text
- `instruction_prompt.py`: sample instruction-style prompt
- `generate_instruction_conversations.py`: runnable script using `generate_conversations(...)`

## Expected Metadata Format

The sample CSV uses these columns:

- `image`: image file name
- `modality`
- `quality`
- `disease`
- `vascular`
- `notes`

Only `image` is required. The other columns are optional, but the generated conversations will be better if you provide more structured hidden metadata.

## How To Use

1. Copy `metadata_template.csv` and replace the sample rows with your own images and metadata.
2. Put your retinal images in one directory.
3. Run:

```bash
cd Instruction
python3 sample/generate_instruction_conversations.py \
  --metadata-csv sample/metadata_template.csv \
  --image-dir /path/to/your/images \
  --output-jsonl sample/generated_instruction_conversations.jsonl
```

## What This Sample Does

It follows the same core method as the main pipeline:

1. build a hidden description with a `desc` class
2. append a task prompt
3. send the hidden description and image to the API
4. save the generated instruction conversations as JSONL

## Adapting It

If your metadata schema is different, only two places usually need changes:

- `user_dataset_desc.py`: map your metadata columns into the hidden description string
- `instruction_prompt.py`: define the conversation style you want
