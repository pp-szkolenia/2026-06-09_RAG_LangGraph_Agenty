from typing import Annotated
from pydantic import Field
from fastmcp.prompts import prompt, Message


@prompt(
    name="Sum of n-th numbers pair",
    description="Prompt which explains how to sum the n-th numbers pair"
)
def sum_of_nth_numbers_pair(
    index: Annotated[int, Field(description="Index of the numbers pair in the data object")]
):
    return [Message(
        role="user",
        content=f"""Load numerical data and take the numbers pair with index {index}. Remember \
that indexing starts with 0. Then find and use the proper tool to sum the numbers together.
                    
If the index is invalid (e.g. too big or negative) return null
"""
    )]
