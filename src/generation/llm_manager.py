"""
LLM management module with support for multiple providers and fallback systems.
"""

import os
import time
import logging
from typing import Dict, Any, Optional, List, Union, Generator
from langchain_openai import ChatOpenAI, OpenAI
from langchain_anthropic import ChatAnthropic
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
import json

logger = logging.getLogger(__name__)


class LLMCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for LLM operations."""
    
    def __init__(self):
        self.tokens_used = 0
        self.start_time = None
        self.end_time = None
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts running."""
        self.start_time = time.time()
        logger.info("LLM generation started")
    
    def on_llm_end(self, response: Any, **kwargs):
        """Called when LLM ends running."""
        self.end_time = time.time()
        if hasattr(response, 'llm_output') and response.llm_output:
            if 'token_usage' in response.llm_output:
                self.tokens_used = response.llm_output['token_usage'].get('total_tokens', 0)
        logger.info(f"LLM generation completed in {self.end_time - self.start_time:.2f}s")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get callback statistics."""
        return {
            "tokens_used": self.tokens_used,
            "duration": (self.end_time - self.start_time) if self.end_time and self.start_time else None
        }


class LLMManager:
    """Manages multiple LLM providers with fallback support."""
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        primary_model: str = "gpt-4",
        fallback_model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.1,
        max_tokens: int = 1000,
        timeout: int = 30
    ):
        """
        Initialize LLM manager.
        
        Args:
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
            primary_model: Primary model to use
            fallback_model: Fallback model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        
        # Initialize models
        self.models = {}
        self.callback_handler = LLMCallbackHandler()
        
        # Initialize OpenAI models
        if openai_api_key:
            self._init_openai_models(openai_api_key)
        
        # Initialize Anthropic models
        if anthropic_api_key:
            self._init_anthropic_models(anthropic_api_key)
        
        if not self.models:
            raise ValueError("At least one API key must be provided")
        
        logger.info(f"LLM Manager initialized with models: {list(self.models.keys())}")
    
    def _init_openai_models(self, api_key: str):
        """Initialize OpenAI models."""
        try:
            # Chat models
            self.models["gpt-4"] = ChatOpenAI(
                model="gpt-4",
                openai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                request_timeout=self.timeout,
                callbacks=[self.callback_handler]
            )
            
            self.models["gpt-3.5-turbo"] = ChatOpenAI(
                model="gpt-3.5-turbo",
                openai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                request_timeout=self.timeout,
                callbacks=[self.callback_handler]
            )
            
            # Text completion models
            self.models["text-davinci-003"] = OpenAI(
                model="text-davinci-003",
                openai_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                request_timeout=self.timeout,
                callbacks=[self.callback_handler]
            )
            
            logger.info("OpenAI models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing OpenAI models: {e}")
    
    def _init_anthropic_models(self, api_key: str):
        """Initialize Anthropic models."""
        try:
            self.models["claude-3-sonnet-20240229"] = ChatAnthropic(
                model="claude-3-sonnet-20240229",
                anthropic_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                callbacks=[self.callback_handler]
            )
            
            self.models["claude-3-haiku-20240307"] = ChatAnthropic(
                model="claude-3-haiku-20240307",
                anthropic_api_key=api_key,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
                callbacks=[self.callback_handler]
            )
            
            logger.info("Anthropic models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Anthropic models: {e}")
    
    def generate(
        self,
        prompt: Union[str, List[BaseMessage]],
        model_name: Optional[str] = None,
        use_fallback: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate text using the specified or primary model.
        
        Args:
            prompt: Input prompt or messages
            model_name: Specific model to use (optional)
            use_fallback: Whether to use fallback if primary fails
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary with generated text and metadata
        """
        # Determine which model to use
        if model_name and model_name in self.models:
            models_to_try = [model_name]
        elif self.primary_model in self.models:
            models_to_try = [self.primary_model]
        else:
            models_to_try = list(self.models.keys())
        
        # Add fallback model if requested
        if use_fallback and self.fallback_model in self.models and self.fallback_model not in models_to_try:
            models_to_try.append(self.fallback_model)
        
        last_error = None
        
        for model_name in models_to_try:
            try:
                logger.info(f"Attempting generation with model: {model_name}")
                
                # Prepare generation parameters
                generation_kwargs = {
                    "temperature": kwargs.get("temperature", self.temperature),
                    "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                }
                
                # Generate response
                if isinstance(prompt, str):
                    response = self.models[model_name].generate([prompt], **generation_kwargs)
                else:
                    response = self.models[model_name].generate(prompt, **generation_kwargs)
                
                # Extract generated text
                if hasattr(response, 'generations') and response.generations:
                    generated_text = response.generations[0][0].text
                else:
                    generated_text = str(response)
                
                # Get callback stats
                stats = self.callback_handler.get_stats()
                
                return {
                    "text": generated_text,
                    "model_used": model_name,
                    "success": True,
                    "tokens_used": stats.get("tokens_used", 0),
                    "duration": stats.get("duration", 0),
                    "error": None
                }
                
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_name} failed: {e}")
                continue
        
        # If all models failed
        error_msg = f"All models failed. Last error: {last_error}"
        logger.error(error_msg)
        
        return {
            "text": "I apologize, but I'm unable to generate a response at this time. Please try again later.",
            "model_used": None,
            "success": False,
            "tokens_used": 0,
            "duration": 0,
            "error": error_msg
        }
    
    def generate_stream(
        self,
        prompt: Union[str, List[BaseMessage]],
        model_name: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Generate text with streaming response.
        
        Args:
            prompt: Input prompt or messages
            model_name: Specific model to use (optional)
            **kwargs: Additional generation parameters
            
        Yields:
            Generated text chunks
        """
        # Determine which model to use
        if model_name and model_name in self.models:
            model = self.models[model_name]
        elif self.primary_model in self.models:
            model = self.models[self.primary_model]
        else:
            raise ValueError("No suitable model available")
        
        try:
            # Prepare generation parameters
            generation_kwargs = {
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            }
            
            # Generate streaming response
            if isinstance(prompt, str):
                for chunk in model.stream([prompt], **generation_kwargs):
                    if hasattr(chunk, 'content'):
                        yield chunk.content
                    else:
                        yield str(chunk)
            else:
                for chunk in model.stream(prompt, **generation_kwargs):
                    if hasattr(chunk, 'content'):
                        yield chunk.content
                    else:
                        yield str(chunk)
                        
        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")
            yield f"Error: {e}"
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return list(self.models.keys())
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a specific model."""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        
        info = {
            "name": model_name,
            "type": type(model).__name__,
            "temperature": getattr(model, 'temperature', self.temperature),
            "max_tokens": getattr(model, 'max_tokens', self.max_tokens),
            "timeout": getattr(model, 'request_timeout', self.timeout)
        }
        
        return info
    
    def update_model_parameters(
        self,
        model_name: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None
    ):
        """Update parameters for a specific model."""
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not found")
        
        model = self.models[model_name]
        
        if temperature is not None:
            model.temperature = temperature
        if max_tokens is not None:
            model.max_tokens = max_tokens
        if timeout is not None:
            model.request_timeout = timeout
        
        logger.info(f"Updated parameters for model {model_name}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics for the LLM manager."""
        return {
            "available_models": self.get_available_models(),
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "callback_stats": self.callback_handler.get_stats()
        }

