"""CrewAI Flow orchestration for the content factory.

Pipeline: input guardrail -> ResearchCrew -> ContentCrew -> quality gate with a
router-driven revision loop (max_revisions), then acceptance. Social
generation, the output guardrail, and response assembly happen in the caller
(MainContentFlow) after the flow completes.

The revision loop uses two routers (quality_gate after the initial review,
quality_gate_again after each re-review) because a single router with an
or_() listener does not re-fire reliably in this crewai version — see the
Flow API verification notes in AGENTS.md.
"""

from crewai.flow.flow import Flow, start, listen, router

from backend.crews.content_crew import ContentCrew
from backend.crews.quality_crew import QualityCrew
from backend.crews.research_crew import ResearchCrew
from backend.guardrails.input_guardrail import validate_input_prompt
from backend.models.draft import DraftContent
from backend.models.state import FlowState
from backend.observability.logger import get_logger
from backend.observability.tracer import trace_execution

logger = get_logger("crew_flow")


class InputGuardrailRejected(Exception):
    """Raised when the input guardrail rejects the topic; carries the guardrail message."""

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ContentFactoryFlow(Flow[FlowState]):
    """CrewAI Flow with a router-based quality/revision loop."""

    @start()
    def validate(self):
        valid, msg = validate_input_prompt(self.state.topic)
        trace_execution("input_guardrail", {"topic": self.state.topic, "valid": valid})
        if not valid:
            self.state.status = "failed_security_guardrail"
            self.state.error_message = msg
            logger.warning(f"Security guardrail rejected prompt: {msg}")
            raise InputGuardrailRejected(msg)

    @listen(validate)
    def research(self):
        self.state.research = ResearchCrew(self.state.topic).run()
        trace_execution("researcher", {"topic": self.state.topic, "sources": len(self.state.research.sources)})

    @listen(research)
    def draft(self):
        self.state.draft = ContentCrew(self.state.topic, self.state.research).run()
        trace_execution("writer", {"title": self.state.draft.title, "word_count": self.state.draft.word_count})

    @listen(draft)
    def review(self):
        critique, fact_check = QualityCrew(self.state.topic, self.state.research).review(self._current_draft())
        self.state.critique = critique
        self.state.fact_check = fact_check
        trace_execution("quality_review", {"approved": critique.approved, "passed": fact_check.passed})

    @router(review)
    def quality_gate(self):
        return self._route()

    @listen("revise")
    def apply_revision(self):
        self.state.revision_count += 1
        logger.info(f"Self-correcting revision loop iteration {self.state.revision_count}/{self.state.max_revisions}")
        edited = QualityCrew(self.state.topic, self.state.research).edit(
            self._current_draft(), self.state.critique, self.state.revision_count
        )
        self.state.edited = edited
        trace_execution("editor", {"revision": self.state.revision_count, "word_count": edited.word_count})

    @listen(apply_revision)
    def re_review(self):
        critique, fact_check = QualityCrew(self.state.topic, self.state.research).review(self._current_draft())
        self.state.critique = critique
        self.state.fact_check = fact_check
        trace_execution(
            "quality_re_review",
            {"revision": self.state.revision_count, "approved": critique.approved, "passed": fact_check.passed},
        )

    @router(re_review)
    def quality_gate_again(self):
        return self._route()

    @listen("accept")
    def accepted(self):
        self.state.status = "quality_approved"
        logger.info("Quality gate accepted content")

    def _current_draft(self) -> DraftContent:
        if self.state.edited:
            return DraftContent(
                title=self.state.edited.title,
                body=self.state.edited.body,
                word_count=self.state.edited.word_count,
            )
        return self.state.draft

    def _route(self) -> str:
        accepted = (
            self.state.fact_check.passed and self.state.critique.approved
        ) or self.state.revision_count >= self.state.max_revisions
        return "accept" if accepted else "revise"
