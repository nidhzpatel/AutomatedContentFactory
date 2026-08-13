import asyncio
from backend.flows.main_flow import MainContentFlow


def test_main_content_flow_execution():
    flow = MainContentFlow(topic="Artificial Intelligence")
    result = asyncio.run(flow.execute())
    assert result["status"] == "completed"
    assert result["topic"] == "Artificial Intelligence"
    assert "metrics" in result
    assert "fact_check_score" in result["metrics"]
