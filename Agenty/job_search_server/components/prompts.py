from fastmcp.prompts import Message, prompt


@prompt(
    name="create_search_filters",
    description=(
        "Analyze the candidate's expectations which are described in a resource. Based on them "
        "create filters for the search url"
    ),
)
def create_search_filters(job_expectations: str) -> list[Message]:
    return [
        Message(
            role="user",
            content=(
                f"""Here are the candidates job expectations:
    {job_expectations}
    
    Filters should be compatible with the following pydantic class:
    
    class JobSearchFilters(BaseModel):
        work_model: Optional[str] = None  # "hybrid" / "praca-zdalna"
        technologies: list[str] = [] # "Python" / "C++" / "C#" / "Java" / "JavaScript" / "TypeScript"
        salary_range: list[int] = []  # <salary_min> / <salary_max>
        sort: Optional[str] = None


    Create dictionary with job search filters in the above format. 

    """
            ),
        )
    ]