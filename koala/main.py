"""프로그램 진입점"""

import os
import sys
from pathlib import Path


PROJECT_ROOT = str(Path(__file__).parent.parent)
sys.path.append(PROJECT_ROOT)


async def main():
    ...


if __name__ == '__main__':
    main()