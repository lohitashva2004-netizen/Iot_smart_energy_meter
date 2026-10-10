"""Keep the README's headline study numbers in sync with the generated study document."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_readme_study_table_matches_generated_doc():
    study = (ROOT / "docs" / "measurement_study.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    row = next(line for line in study.splitlines() if line.startswith("| 5 W |"))
    cells = [c.strip() for c in row.strip("|").split("|")]
    apparent, real = cells[4], cells[5]            # Vrms x Irms error, mean(v.i) error
    assert apparent in readme and real in readme
