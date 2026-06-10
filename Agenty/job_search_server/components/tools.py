import json
import requests
import urllib.parse
from typing import Optional
from pydantic import BaseModel
from bs4 import BeautifulSoup
from fastmcp.tools import tool


class JobSearchFilters(BaseModel):
    work_model: Optional[str] = None
    technologies: list[str] = []
    salary_range: list[int] = []
    sort: Optional[str] = None
    extra: dict[str, str] = {}


@tool
def generate_search_url(filters: JobSearchFilters) -> str:
    path = ["pl"]
    if filters.work_model:
        path.append(filters.work_model)

    t_map = {"C++": "C%2B%2B", "C#": "C%23"}
    techs = [t_map.get(t, str(t)) for t in filters.technologies]

    if techs:
        path.append(techs[0])

    url = "https://nofluffjobs.com/" + "/".join(path)

    criteria = []
    sr = filters.salary_range
    if len(sr) == 2:
        criteria.extend([f"salary>pln{sr[0]}m", f"salary<pln{sr[1]}m"])

    if len(techs) > 1:
        criteria.append("requirement=" + ",".join(techs[1:]))

    for k, v in filters.extra.items():
        criteria.append(f"{k}={v}")

    query_params = []
    if criteria:
        qs = urllib.parse.quote(" ".join(criteria), safe=',%')
        query_params.append(f"criteria={qs}")

    if filters.sort:
        query_params.append(f"sort={filters.sort}")

    if query_params:
        url += "?" + "&".join(query_params)

    return url
