# This file is to handle interactions with the OpenAI LLM client.
# It includes functions to call the LLM with a prompt and return the response.
import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load .env file 
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
  raise ValueError("OPENAI_API_KEY not found in environment variables.")

client = AsyncOpenAI(api_key=openai_api_key)

# Function to call the LLM with a prompt
async def call_llm(prompt: str, model: str = "gpt-3.5-turbo") -> str:
  """
  Calls OpenAI LLM with the given prompt.
  
  Args:
      prompt (str): The input prompt to send to the model.
      model (str): Model name to use.

  Returns:
      str: The response text from the LLM.
  """
  try:
      response = await client.chat.completions.create(
        model=model,
        messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": prompt}
        ],
        temperature=0  # deterministic output for keyword extraction
      )
      return response.choices[0].message.content
  except Exception as e:
    raise RuntimeError(f"LLM call failed: {str(e)}")
