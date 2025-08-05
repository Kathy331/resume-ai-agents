import pytest
from agents.keyword_extractor.agent import KeywordExtractorAgent
from agents.base_agent import AgentInput
import os

## To run this test, ensure you have pytest installed and run `pytest tests/test_agents/test_keyword_extractor.py`
@pytest.mark.asyncio
async def test_keyword_extractor():
    agent = KeywordExtractorAgent(config={})
    input_text = "Jane is a software engineer at Google focusing on AI and ML."
    input_data = AgentInput(data={"text": input_text})

    result = await agent.execute(input_data)
    assert result.success

    # Prepare output folder
    output_dir = "outputs"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "test_keyword_extractor_output.txt")

    # Write input and output to the file
    with open(output_file, "w") as f:
        f.write("=== Keyword Extractor Test Result ===\n")
        f.write(f"Input Text:\n{input_text}\n\n")
        f.write(f"Output Keywords:\n{result.data['keywords']}\n")
        f.write("\nFull Result Object:\n")
        f.write(str(result.model_dump()))

    print(f"Test output written to: {output_file}")
