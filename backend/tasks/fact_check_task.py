from crewai import Task

from backend.agents.fact_checker import create_fact_checker_agent


def create_fact_check_task(topic: str, draft_body: str, research_summary: str) -> Task:
    """Task for the fact-checker agent: audit claims against research context."""
    return Task(
        description=(
            f"Audit the factual claims in the following article about '{topic}' "
            f"against this research context:\n{research_summary[:800]}\n\n"
            f"ARTICLE:\n{draft_body[:1200]}\n\n"
            "Respond in EXACTLY this format:\n"
            "VERDICT: PASS or FAIL\n"
            "CLAIMS:\n"
            "- [VERIFIED] <claim>\n"
            "- [UNVERIFIED] <claim>"
        ),
        expected_output="VERDICT plus a list of [VERIFIED]/[UNVERIFIED] claims.",
        agent=create_fact_checker_agent(),
    )
