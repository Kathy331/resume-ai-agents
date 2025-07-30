import pytest
import os
from agents.entity_extractor.agent import EntityExtractor
from agents.base_agent import AgentInput

@pytest.mark.asyncio
async def test_entity_extractor():
    agent = EntityExtractor(config={})
    input_text = """Hi John, your interview for the position of Software Engineer at OpenAI is scheduled on August 10, 2025 at 3:00 PM.
Interview with: Jane Doe"""
    input_data = AgentInput(data={"text": input_text})

    result = await agent.execute(input_data)
    assert result.success

    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_entity_extractor_output.txt")

    with open(output_file, "w") as f:
        f.write("=== Entity Extractor Test Result ===\n\n")
        f.write("Input Text:\n")
        f.write(input_text + "\n\n")

        f.write("Extracted Information:\n")
        f.write(f"Company: {result.data.get('company', 'N/A')}\n")
        f.write(f"Role: {result.data.get('role', 'N/A')}\n")
        f.write(f"Interview Date & Time: {result.data.get('interview_datetime', 'N/A')}\n")
        f.write(f"Interviewer: {result.data.get('interviewer', 'N/A')}\n")

        f.write("\nFull Result Object:\n")
        f.write(str(result.model_dump()))

    print(f"Entity extraction output written to: {output_file}")
