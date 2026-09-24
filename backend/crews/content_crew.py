from crewai import Crew, Process

from backend.models.draft import DraftContent
from backend.models.research import ResearchOutput
from backend.tasks.write_task import create_write_task
from backend.observability.logger import get_logger

logger = get_logger("content_crew")


class ContentCrew:
    """CrewAI crew that drafts the article from a ResearchOutput."""

    def __init__(self, topic: str, research: ResearchOutput):
        self.topic = topic
        self.research = research

    def run(self) -> DraftContent:
        task = create_write_task(self.topic, self.research.summary)
        crew = Crew(agents=[task.agent], tasks=[task], process=Process.sequential, verbose=False, memory=False)
        result = crew.kickoff()
        return self._parse_result(str(result))

    def _parse_result(self, text: str) -> DraftContent:
        content = text.strip()
        if len(content) < 50:
            raise ValueError("ContentCrew produced unusable output")

        lines = content.splitlines()
        title = lines[0].replace("#", "").strip() if lines else f"Guide to {self.topic}"
        if not title:
            title = f"Guide to {self.topic}"

        return DraftContent(title=title, body=content, word_count=len(content.split()))
