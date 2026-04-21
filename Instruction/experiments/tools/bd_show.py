from pathlib import Path
import sys

INSTRUCTION_ROOT = Path(__file__).resolve().parents[2]
if str(INSTRUCTION_ROOT) not in sys.path:
    sys.path.insert(0, str(INSTRUCTION_ROOT))

from tools.bounding_box.visualize import main


if __name__ == "__main__":
    main()
