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


@prompt(
    name="analyze_job_fit",
    description=(
        "Analyze the candidate's CV retrieved from resources and compare it to the job offer. "
        "This prompt takes a job description (job_description) and the CV content (resume_text)."
    ),
)
def analyze_job_fit(job_description: str, resume_text: str) -> list[Message]:
    return [
        Message(
            role="user",
            content=(
                "You are a career advisor. You analyze how well a job offer matches a candidate's CV.\n"
                "Return the fit assessment in three points:\n"
                "1. Overall fit (1-10) with a brief explanation.\n"
                "2. Candidate's strengths in the context of this offer (briefly listed).\n"
                "3. Missing elements in the candidate's CV (briefly listed)."
            ),
        ),
        Message(
            role="user",
            content=f"Job offer:\n{job_description}\n\nCV content:\n{resume_text}",
        ),
    ]
