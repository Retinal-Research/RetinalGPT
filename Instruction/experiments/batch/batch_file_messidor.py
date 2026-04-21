from pathlib import Path
import sys

INSTRUCTION_ROOT = Path(__file__).resolve().parents[2]
if str(INSTRUCTION_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUCTION_ROOT))

from batch_runner import run_named_batch_job


def create_batch_file():
    run_named_batch_job("Messidor")


if __name__ == "__main__":
    create_batch_file()
