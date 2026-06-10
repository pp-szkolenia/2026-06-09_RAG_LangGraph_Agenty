import fitz
from pathlib import Path
from fastmcp.resources import resource


@resource(
    "data://job_expectations",
    name="Job expectations description",
    description="Candidate's job expectations including, work mode, and salary range"
)
def job_expectations():
    current_dir = Path(__file__).parent
    file_path = current_dir / "job_expectations.txt"
    return file_path.read_text(encoding="utf-8")


@resource(
    "data://resume",
    name="Candidate resume",
    description="Resume loaded from .pdf file with text extracted"
)
def candidate_resume() -> str:
    current_dir = Path(__file__).parent
    file_path = current_dir / "Jack Duck – resume.pdf"

    doc = fitz.open(file_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text

