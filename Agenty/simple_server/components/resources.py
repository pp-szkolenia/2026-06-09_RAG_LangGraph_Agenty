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
