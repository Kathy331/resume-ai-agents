from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel

class AgentInput(BaseModel):
  """Standard input format for all agents"""
  data: Dict[str, Any] # Input data for the agent, in a dictionary format, key value pairs
  metadata: Optional[Dict[str, Any]] = None # Additional metadata about the input (e.g., source, timestamp)
  previous_agent_output: Optional[Dict[str, Any]] = None # Output from a previous agent, if needed for context

class AgentOutput(BaseModel):
  """Standard output format for all agents"""
  success: bool # Indicates if the agent executed successfully
  data: Dict[str, Any] # Output data from the agent, in a dictionary format
  metadata: Dict[str, Any] # Additional metadata about the output (e.g., processing time, source)
  errors: Optional[list] = None # List of errors encountered during execution, if any
  next_agent_suggestions: Optional[list] = None # Suggestions for next agents to handle the output, if applicable

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