from crewai import Task

from backend.agents.critic import create_critic_agent


def create_critic_task(draft_body: str) -> Task:
    """Task for the critic agent: score and approve/reject a draft."""
    return Task(
        description=(
            f"Critique the following draft article for clarity, structure, and quality:\n{draft_body[:1000]}\n\n"
            "Respond in EXACTLY this format:\n"
            "CLARITY: <number 0-10>\n"
            "ENGAGEMENT: <number 0-10>\n"
            "APPROVED: YES or NO\n"
            "SUGGESTIONS:\n"
            "- <specific improvement>\n"
            "- <specific improvement>"
        ),
        expected_output="CLARITY / ENGAGEMENT / APPROVED / SUGGESTIONS structured critique.",
        agent=create_critic_agent(),
    )
