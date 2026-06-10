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


@tool
def get_offers_from_search_url(search_url: str) -> list[str]:
    response = requests.get(search_url, headers={"User-Agent": "."})
    # print(response.url)
    soup = BeautifulSoup(response.text, "lxml")

    if soup.find("nfj-no-offers-found-header"):
        return []

    all_slugs = []
    for item in soup.find_all("nfj-postings-list", {"data-cy-params": '{"search_results":"standard"}'}):
        all_links = item.find_all("a")
        for link in all_links:
            if link["href"].startswith("/pl/job"):
                all_slugs.append(link["href"])

    return [urllib.parse.urljoin("https://nofluffjobs.com", slug) for slug in all_slugs] #+ [response.url]


@tool
def scrape_single_offer(url: str) -> dict:
    response = requests.get(url, headers={"User-Agent": "."})
    soup = BeautifulSoup(response.text, "lxml")
    all_data = json.loads(soup.find("script", {"id": "serverApp-state"}).text)
    data_key = next((key for key in all_data.keys() if key.startswith("/posting/")), None)
    data = all_data[data_key]

    company_name = data.get("company", {}).get("name", "")
    company_size = data.get("company", {}).get("size", "")
    job_category = data.get("basics", {}).get("category", "")
    seniority = ", ".join(data.get("basics", {}).get("seniority", []))
    contract_start = data.get("essentials", {}).get("contract", {}).get("start", "")

    salary_data = data.get("essentials", {}).get("originalSalary", {})
    currency = salary_data.get("currency", "")
    salary_info = "\n".join([
        f"{t.upper()}: {info['range'][0]}-{info['range'][1]} {currency} / {info['period']}"
        for t, info in salary_data.get("types", {}).items()
        if "range" in info
    ])

    job_description = data.get("details", {}).get("description", "")
    job_location = " / ".join(
        [item.get("city", "") for item in data.get("location", {}).get("places", [])])
    must_have_skills = " | ".join(
        [skill.get("value", "") for skill in data.get("requirements", {}).get("musts", [])])
    nice_to_have_skills = " | ".join(
        [skill.get("value", "") for skill in data.get("requirements", {}).get("nices", [])])
    requirements_description = data.get("requirements", {}).get("description", "")

    return {
        "company_name": company_name,
        "company_size": company_size,
        "job_category": job_category,
        "seniority": seniority,
        "contract_start": contract_start,
        "salary_info": salary_info,
        "job_description": job_description,
        "job_location": job_location,
        "must_have_skills": must_have_skills,
        "nice_to_have_skills": nice_to_have_skills,
        "requirements_description": requirements_description,
    }
