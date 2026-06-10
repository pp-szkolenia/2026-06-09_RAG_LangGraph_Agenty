from typing import Annotated
from pydantic import Field
from fastmcp.tools import tool


@tool(description="This function takes two numbers/strings and returns their sum")
def add(
    a: Annotated[float | str, Field(description="The first item")],
    b: Annotated[float | str, Field(description="The second item")]
):
    return a + b


@tool(description="This function takes two numbers and returns their difference")
def subtract(
    a: Annotated[float, Field(description="The first number")],
    b: Annotated[float, Field(description="The second number")],
) -> float:
    return a - b
