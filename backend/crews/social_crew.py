from crewai import Crew, Process

from backend.tasks.social_task import create_linkedin_task, create_overview_task, create_x_task
from backend.observability.logger import get_logger

logger = get_logger("social_crew")

MIN_POST_LENGTH = 20


class SocialCrew:
    """CrewAI crew that generates the LinkedIn, X, and overview formats."""

    def __init__(self, topic: str):
        self.topic = topic

    def run(self) -> dict:
        tasks = [
            create_linkedin_task(self.topic),
            create_x_task(self.topic),
            create_overview_task(self.topic),
        ]
        crew = Crew(
            agents=[tasks[0].agent],
            tasks=tasks,
            process=Process.sequential,
            verbose=False,
            memory=False,
        )
        crew.kickoff()

        result = {
            "linkedin": str(tasks[0].output.raw) if tasks[0].output else "",
            "x_post": str(tasks[1].output.raw) if tasks[1].output else "",
            "overview": str(tasks[2].output.raw) if tasks[2].output else "",
        }
        if any(len(text.strip()) < MIN_POST_LENGTH for text in result.values()):
            raise ValueError("SocialCrew produced unusable output")

        logger.info(f"SocialCrew completed (linkedin={len(result['linkedin'])} chars, x={len(result['x_post'])} chars)")
        return result
