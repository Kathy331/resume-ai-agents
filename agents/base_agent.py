from abc import ABC, abstractmethod
from typing import Dict, Any
from shared.models import AgentInput, AgentOutput

class BaseAgent(ABC):
  def __init__(self, config: Dict[str, Any]): 
    self.config = config # Configuration for the agent, can include API keys, settings, etc.
    self.name = self.__class__.__name__ # Name of the agent class, used for identification
  
  @abstractmethod
  async def execute(self, input_data: AgentInput) -> AgentOutput: 
    """Main execution method - each agent implements this"""
    pass
  
  @abstractmethod
  def validate_input(self, input_data: AgentInput) -> bool: 
    """Validate input data format"""
    pass
  
  def preprocess(self, input_data: AgentInput) -> AgentInput:
    """Optional preprocessing step"""
    return input_data
  
  def postprocess(self, output: AgentOutput) -> AgentOutput:
    """Optional postprocessing step"""
    return output