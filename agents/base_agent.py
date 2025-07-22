from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentInput(BaseModel):
  """Standard input format for all agents"""
  data: Dict[str, Any]
  metadata: Optional[Dict[str, Any]] = None
  previous_agent_output: Optional[Dict[str, Any]] = None

class AgentOutput(BaseModel):
  """Standard output format for all agents"""
  success: bool
  data: Dict[str, Any]
  metadata: Dict[str, Any]
  errors: Optional[list] = None
  next_agent_suggestions: Optional[list] = None

class BaseAgent(ABC):
  def __init__(self, config: Dict[str, Any]):
    self.config = config
    self.name = self.__class__.__name__
  
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