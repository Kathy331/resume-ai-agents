from agents.base_agent import BaseAgent, AgentInput, AgentOutput
from agents.keyword_extractor.config import PROMPT_TEMPLATE
from shared.llm_client import call_llm  #could be wrapper for OpenAI/Tavily, but so far is just OpenAI

# Import EmailKeywordExtractor from the specialized email module
from agents.keyword_extractor.agent_email import EmailKeywordExtractor

class KeywordExtractorAgent(BaseAgent):
  def validate_input(self, input_data: AgentInput) -> bool:
    return "text" in input_data.data and bool(input_data.data["text"].strip())
  
  async def execute(self, input_data: AgentInput) -> AgentOutput:
    text = input_data.data["text"]
    prompt = PROMPT_TEMPLATE.format(text=text)

    # Call your llm client with the prompt and API key (assumed loaded in llm_client)
    try:
        llm_response = await call_llm(prompt)
        keywords = llm_response.strip()
        return AgentOutput(
            success=True,
            data={"keywords": keywords},
            metadata={},
            errors=None
        )
    except Exception as e:
        return AgentOutput(
            success=False,
            data={},
            metadata={},
            errors=[str(e)]
        )
