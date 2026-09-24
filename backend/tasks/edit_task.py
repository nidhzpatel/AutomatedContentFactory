from crewai import Task

from backend.agents.editor import create_editor_agent


def create_edit_task(topic: str, draft_body: str, suggestions: list) -> Task:
    """Task for the editor agent: revise the draft against feedback."""
    return Task(
        description=(
            f"Refine and edit the article draft for '{topic}'. "
            f"Address this feedback: {list(suggestions)}.\n"
            f"Current draft:\n{draft_body}"
        ),
        expected_output=(
            "The full revised article in Markdown. The first line must be the title "
            "as a markdown header, followed by the revised body."
        ),
        agent=create_editor_agent(),
    )
