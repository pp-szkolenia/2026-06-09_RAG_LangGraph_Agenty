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
