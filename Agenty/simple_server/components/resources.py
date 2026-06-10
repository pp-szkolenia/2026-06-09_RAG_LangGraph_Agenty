import json
from pathlib import Path
from fastmcp.resources import resource


@resource(
    "data://numbers",
    name="Numerical data",
    description="Numerical input data"
)
def number_data():
    with open(Path(__file__).parent / "data_1.json") as f:
        data = json.load(f)
    return json.dumps(data)


@resource(
    "data://strings",
    name="Text data",
    description="Text input data"
)
def text_data() -> str:
    current_dir = Path(__file__).parent
    file_path = current_dir / "data_2.json"

    with open(file_path, "r") as f:
        data = json.load(f)
    return json.dumps(data)
