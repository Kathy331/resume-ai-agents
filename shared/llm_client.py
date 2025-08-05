# This file is to handle interactions with the OpenAI LLM client.
# It includes functions to call the LLM with a prompt and return the response.
import os
from openai import AsyncOpenAI, OpenAI
from dotenv import load_dotenv
from .openai_cache import OpenAICache
from typing import Optional

# Load .env file 
load_dotenv()

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
  print("⚠️  OPENAI_API_KEY not found in environment variables. Using cache-only mode.")
  openai_api_key = "dummy-key-for-cache-only"

async_client = AsyncOpenAI(api_key=openai_api_key) if openai_api_key != "dummy-key-for-cache-only" else None
sync_client = OpenAI(api_key=openai_api_key) if openai_api_key != "dummy-key-for-cache-only" else None

# Initialize cache
openai_cache = OpenAICache()


class LLMClient:
    """Synchronous LLM client wrapper for interview prep intelligence with caching"""
    
    def __init__(self, model: str = "gpt-4o-mini", use_cache: bool = True):
        self.model = model
        self.client = sync_client
        self.use_cache = use_cache
        self.cache = openai_cache if use_cache else None
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, company_name: Optional[str] = None) -> str:
        """
        Generate text using OpenAI LLM with caching support
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature for generation
            company_name: Optional company name for cache tracking
            
        Returns:
            Generated text response
        """
        # Check cache first if enabled
        if self.use_cache and self.cache:
            cached_response = self.cache.get(prompt, self.model, max_tokens, temperature)
            if cached_response:
                print(f"🗄️ Using cached response for {company_name or 'query'}")
                return cached_response
        
        # If no OpenAI client available and no cache hit, return mock response
        if not self.client:
            mock_response = self._generate_mock_response(prompt, company_name)
            print(f"🤖 Using mock response for {company_name or 'query'} (no API key)")
            
            # Cache the mock response
            if self.use_cache and self.cache:
                self.cache.set(prompt, self.model, max_tokens, temperature, mock_response, company_name)
            
            return mock_response
        
        try:
            # Make API call
            print(f"🌐 Making OpenAI API call for {company_name or 'query'}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates structured responses for interview preparation."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            response_text = response.choices[0].message.content
            
            # Cache the response
            if self.use_cache and self.cache:
                self.cache.set(prompt, self.model, max_tokens, temperature, response_text, company_name)
            
            return response_text
            
        except Exception as e:
            print(f"❌ OpenAI API error: {str(e)}")
            # Fallback to mock response
            mock_response = self._generate_mock_response(prompt, company_name)
            
            # Cache the mock response
            if self.use_cache and self.cache:
                self.cache.set(prompt, self.model, max_tokens, temperature, mock_response, company_name)
            
            return mock_response
    
    def _generate_mock_response(self, prompt: str, company_name: Optional[str] = None) -> str:
        """Generate mock response for testing when API is not available"""
        
        # Detect what kind of analysis is being requested
        prompt_lower = prompt.lower()
        
        if "company insights" in prompt_lower or "analyze the company" in prompt_lower:
            return self._mock_company_analysis(company_name or "the company")
        elif "interviewer" in prompt_lower:
            return self._mock_interviewer_analysis(company_name or "Unknown")
        elif "questions" in prompt_lower and "generate" in prompt_lower:
            return self._mock_questions_generation(company_name or "the company")
        elif "prep summary" in prompt_lower or "preparation package" in prompt_lower:
            return self._mock_prep_summary(company_name or "the company")
        else:
            return f"Mock response for analysis request about {company_name or 'the subject'}. This is a placeholder response generated without API access."
    
    def _mock_company_analysis(self, company_name: str) -> str:
        """Mock company analysis response"""
        return f"""Based on available research about {company_name}:

**Company Overview:**
- {company_name} is focused on innovation and growth in their sector
- Strong emphasis on sustainability and social impact
- Recent expansion into new markets and technologies

**Key Insights:**
- Leadership prioritizes collaboration and innovation
- Company culture values diversity and inclusion
- Recent strategic initiatives focus on digital transformation
- Strong financial position with consistent growth

**Strategic Focus Areas:**
- Technology integration and digital solutions
- Sustainability and environmental responsibility
- Market expansion and customer experience
- Talent development and retention

**Interview Relevance:**
This analysis suggests {company_name} values candidates who demonstrate:
- Innovation and problem-solving skills
- Commitment to sustainability
- Collaborative mindset
- Adaptability to change"""
    
    def _mock_interviewer_analysis(self, company_name: str) -> str:
        """Mock interviewer analysis response"""
        return f"""Interviewer Background Analysis for {company_name}:

**Professional Profile:**
- Senior leader with extensive industry experience
- Background in technology and business development
- Known for mentoring and team building
- Focus on strategic thinking and execution

**Interview Style Expectations:**
- Likely to ask behavioral and situational questions
- Interest in problem-solving approaches
- Values specific examples and concrete results
- May explore cultural fit and collaboration skills

**Key Topics to Prepare:**
- Past project experiences and outcomes
- Leadership and teamwork examples
- Innovation and problem-solving instances
- Questions about company strategy and vision"""
    
    def _mock_questions_generation(self, company_name: str) -> str:
        """Mock question generation response"""
        return f"""Strategic Interview Questions for {company_name}:

**Company Strategy & Vision:**
1. How do you see {company_name}'s mission aligning with current market trends?
2. What attracted you to {company_name}'s approach to innovation?
3. How would you contribute to {company_name}'s sustainability goals?

**Role-Specific & Technical:**
4. Can you walk us through your approach to [relevant technical skill]?
5. How do you handle complex problem-solving in your field?
6. What experience do you have with [relevant technology/process]?

**Behavioral & Cultural:**
7. Tell me about a time you collaborated on a challenging project.
8. How do you approach continuous learning and development?
9. Describe a situation where you had to adapt to significant change.

**Strategic & Forward-Looking:**
10. Where do you see this industry heading in the next 5 years?
11. How would you approach building relationships with key stakeholders?
12. What questions do you have about {company_name}'s future plans?"""
    
    def _mock_prep_summary(self, company_name: str) -> str:
        """Mock preparation summary response"""
        return f"""Interview Preparation Summary for {company_name}:

**Key Talking Points:**
- Emphasize alignment with {company_name}'s mission and values
- Highlight relevant technical skills and experience
- Demonstrate understanding of industry challenges
- Show enthusiasm for company's growth trajectory

**Strategic Recommendations:**
- Prepare specific examples using STAR method
- Research recent company news and developments
- Practice articulating your value proposition
- Prepare thoughtful questions about role and company

**Success Metrics:**
- Clear communication of relevant experience
- Demonstration of cultural fit
- Strong examples of problem-solving ability
- Genuine interest in company's future

**Final Preparation Notes:**
Review your resume thoroughly, practice common behavioral questions, and ensure you can discuss your experience in the context of {company_name}'s needs and objectives."""


def get_llm_client(model: str = "gpt-4o-mini") -> LLMClient:
    """Get an LLM client instance"""
    return LLMClient(model=model)


# Function to call the LLM with a prompt (async version)
async def call_llm(prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 1000, temperature: float = 0.0) -> str:
  """
  Calls OpenAI LLM with the given prompt, with caching and fallback support.
  
  Args:
      prompt (str): The input prompt to send to the model.
      model (str): Model name to use.
      max_tokens (int): Maximum tokens to generate.
      temperature (float): Temperature for response variability.

  Returns:
      str: The response text from the LLM.
  """
  # Check if caching is disabled via environment variable
  disable_cache = os.getenv('DISABLE_OPENAI_CACHE', '').lower() == 'true'
  
  # Check cache first (unless disabled)
  if not disable_cache and openai_cache:
      cached_response = openai_cache.get(prompt, model, max_tokens, temperature)
      if cached_response:
          print(f"🗄️ Using cached response for async call")
          return cached_response
  
  # If no async client available, use mock response
  if not async_client:
      print(f"🤖 Using mock response for async call (no API key)")
      mock_response = f"Mock keyword extraction result for prompt: {prompt[:100]}..."
      
      # Cache the mock response (unless caching disabled)
      if not disable_cache and openai_cache:
          openai_cache.set(prompt, model, max_tokens, temperature, mock_response, "async_call")
      
      return mock_response
  
  try:
      if disable_cache:
          print(f"🌐 Making async OpenAI API call (cache disabled)")
      else:
          print(f"🌐 Making async OpenAI API call")
      
      response = await async_client.chat.completions.create(
        model=model,
        messages=[
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=temperature
      )
      
      response_text = response.choices[0].message.content
      
      # Cache the response (unless caching disabled)
      if not disable_cache and openai_cache:
          openai_cache.set(prompt, model, max_tokens, temperature, response_text, "async_call")
      elif disable_cache:
          print(f"💾 Caching disabled - response not cached")
      
      return response_text
      
  except Exception as e:
    print(f"❌ Async OpenAI API error: {str(e)}")
    # Fallback to mock response
    mock_response = f"Mock fallback result for prompt: {prompt[:100]}..."
    
    # Cache the mock response (unless caching disabled)
    if not disable_cache and openai_cache:
        openai_cache.set(prompt, model, max_tokens, temperature, mock_response, "async_call_fallback")
    
    return mock_response
