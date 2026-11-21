#!/usr/bin/env python3
"""Copy the bundled passport artwork to the grader's output path."""

import os
from pathlib import Path


def main() -> None:
    source = Path(__file__).resolve().with_name("entry.png")
    target = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")) / "entry.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(source.read_bytes())
    print(target)


if __name__ == "__main__":
    main()
