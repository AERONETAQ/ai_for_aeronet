"""Section 5 · Skills. One markdown file per skill in this folder.

The number prefix fixes the order they appear in the system prompt; the rest of the file name is the skill
name (01_data_access.md -> "data_access"). The file holds the skill text exactly as the notebook had it
between the triple quotes. To add a skill: add a file. To change one: edit it. No code changes.
"""
from pathlib import Path

SKILLS_DIR = Path(__file__).parent

SKILLS = {}
for path in sorted(SKILLS_DIR.glob("*.md")):
    name = path.stem.split("_", 1)[1]            # "01_data_access" -> "data_access"
    SKILLS[name] = path.read_text()

SKILLS_TEXT = "\n".join(f"### skill: {name}\n{text.strip()}\n" for name, text in SKILLS.items())
