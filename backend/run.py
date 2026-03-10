#!/usr/bin/env python3
"""Prompt for OPENAI_API_KEY if needed, then start the server."""
import os
import subprocess
import sys
from getpass import getpass
from pathlib import Path

def main():
    env_path = Path(__file__).parent / ".env"
    example_path = Path(__file__).parent / ".env.example"

    # Load existing .env if present
    env_content = {}
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    env_content[k.strip()] = v.strip()

    # If no key set, prompt
    if not env_content.get("OPENAI_API_KEY") or env_content.get("OPENAI_API_KEY") == "sk-...":
        try:
            key = getpass("Enter OPENAI_API_KEY (or press Enter to skip): ").strip()
        except EOFError:
            key = ""
        if key:
            env_content["OPENAI_API_KEY"] = key
            # Write .env from example and overlay our key
            if example_path.exists():
                with open(example_path) as f:
                    lines = f.readlines()
                with open(env_path, "w") as f:
                    for line in lines:
                        if line.strip().startswith("OPENAI_API_KEY="):
                            f.write(f"OPENAI_API_KEY={key}\n")
                        else:
                            f.write(line)
            else:
                with open(env_path, "w") as f:
                    f.write(f"OPENAI_API_KEY={key}\n")
            print("Saved to .env")
        else:
            print("No key entered. LLM features will use fallbacks (no intent/response tuning).")

    # Start uvicorn (loads .env via pydantic-settings)
    os.chdir(Path(__file__).parent)
    sys.exit(subprocess.run([sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"], cwd=Path(__file__).parent).returncode)


if __name__ == "__main__":
    main()
