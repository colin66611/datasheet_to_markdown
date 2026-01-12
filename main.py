"""主入口文件"""

import sys
from datasheet_to_markdown.cli import main

if __name__ == "__main__":
    sys.exit(main() or 0)
