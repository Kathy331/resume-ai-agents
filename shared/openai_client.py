#!/usr/bin/env python3
"""
OpenAI Client - Centralized OpenAI API Interface
===============================================

Provides a centralized OpenAI client with caching and error handling
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_openai_client():
    """
    Get configured OpenAI client
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        client = OpenAI(api_key=api_key)
        return client
        
    except ImportError:
        raise ImportError("OpenAI library not installed. Install with: pip install openai")
    except Exception as e:
        raise Exception(f"Failed to initialize OpenAI client: {str(e)}")

def generate_completion(
    messages: list,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Generate completion using OpenAI API
    """
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ OpenAI completion error: {str(e)}")
        return ""

def generate_text(
    prompt: str,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: Optional[int] = None
) -> str:
    """
    Simple text generation function
    """
    messages = [{"role": "user", "content": prompt}]
    return generate_completion(messages, model, temperature, max_tokens)