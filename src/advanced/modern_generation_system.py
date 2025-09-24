"""
Modern Generation System - 2025 State-of-the-Art Implementation
Implements latest generation techniques with hallucination prevention and fact-checking
"""

import asyncio
import logging
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import hashlib
from concurrent.futures import ThreadPoolExecutor

# Core imports
import openai
from anthropic import AsyncAnthropic
import cohere
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from sentence_transformers import SentenceTransformer

# Advanced imports
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.llms import OpenAI, Anthropic

logger = logging.getLogger(__name__)

@dataclass
class GenerationConfig:
    """Configuration for modern generation system"""
    # LLM Configuration
    primary_llm: str = "openai"  # openai, anthropic, cohere, local
    fallback_llms: List[str] = None
    
    # Model settings
    openai_model: str = "gpt-4o"
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    cohere_model: str = "command-r-plus"
    
    # Generation parameters
    temperature: float = 0.1  # Low temperature for factual responses
    max_tokens: int = 2000
    top_p: float = 0.9
    frequency_penalty: float = 0.1
    presence_penalty: float = 0.1
    
    # Hallucination prevention
    enable_fact_checking: bool = True
    enable_citation_verification: bool = True
    enable_confidence_scoring: bool = True
    confidence_threshold: float = 0.7
    
    # Response quality
    enable_response_validation: bool = True
    enable_source_attribution: bool = True
    enable_uncertainty_handling: bool = True
    
    # Performance
    timeout_seconds: int = 30
    max_retries: int = 3
    batch_size: int = 1

class ModernGenerationSystem:
    """
    State-of-the-art generation system with hallucination prevention:
    - Multi-LLM orchestration with fallbacks
    - Fact-checking and citation verification
    - Confidence scoring and uncertainty handling
    - Response validation and quality control
    - Source attribution and transparency
    """
    
    def __init__(self, config: GenerationConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize LLM clients
        self._initialize_llm_clients()
        
        # Initialize fact-checking components
        if self.config.enable_fact_checking:
            self._initialize_fact_checking()
        
        # Initialize response validation
        if self.config.enable_response_validation:
            self._initialize_response_validation()
        
        self.logger.info("Modern Generation System initialized with hallucination prevention")
    
    def _initialize_llm_clients(self):
        """Initialize LLM clients with proper configuration"""
        try:
            self.llm_clients = {}
            
            # OpenAI client
            if self.config.primary_llm == "openai" or "openai" in (self.config.fallback_llms or []):
                self.llm_clients["openai"] = openai.AsyncOpenAI(
                    api_key=openai.api_key,
                    timeout=self.config.timeout_seconds
                )
            
            # Anthropic client
            if self.config.primary_llm == "anthropic" or "anthropic" in (self.config.fallback_llms or []):
                self.llm_clients["anthropic"] = AsyncAnthropic(
                    api_key=os.getenv("ANTHROPIC_API_KEY"),
                    timeout=self.config.timeout_seconds
                )
            
            # Cohere client
            if self.config.primary_llm == "cohere" or "cohere" in (self.config.fallback_llms or []):
                self.llm_clients["cohere"] = cohere.AsyncClient(
                    api_key=os.getenv("COHERE_API_KEY")
                )
            
            # Local model (if available)
            if self.config.primary_llm == "local" or "local" in (self.config.fallback_llms or []):
                self._initialize_local_model()
            
            self.logger.info(f"Initialized LLM clients: {list(self.llm_clients.keys())}")
            
        except Exception as e:
            self.logger.error(f"Error initializing LLM clients: {e}")
            raise
    
    def _initialize_local_model(self):
        """Initialize local model for offline generation"""
        try:
            # Use a lightweight model for local generation
            model_name = "microsoft/DialoGPT-medium"
            self.local_tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.local_model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Add padding token
            if self.local_tokenizer.pad_token is None:
                self.local_tokenizer.pad_token = self.local_tokenizer.eos_token
            
            self.llm_clients["local"] = {
                "tokenizer": self.local_tokenizer,
                "model": self.local_model
            }
            
            self.logger.info("Local model initialized")
            
        except Exception as e:
            self.logger.warning(f"Local model initialization failed: {e}")
    
    def _initialize_fact_checking(self):
        """Initialize fact-checking components"""
        try:
            # Initialize sentence transformer for similarity checking
            self.fact_checker = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            
            # Initialize fact-checking patterns
            self.fact_patterns = {
                'dates': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
                'numbers': r'\b\d+(?:\.\d+)?\b',
                'percentages': r'\b\d+(?:\.\d+)?%\b',
                'quotes': r'"[^"]*"',
                'citations': r'\[[^\]]+\]',
                'urls': r'https?://[^\s]+'
            }
            
            self.logger.info("Fact-checking components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing fact-checking: {e}")
    
    def _initialize_response_validation(self):
        """Initialize response validation components"""
        try:
            # Initialize validation patterns
            self.validation_patterns = {
                'hallucination_indicators': [
                    r'\b(?:I think|I believe|I assume|probably|maybe|perhaps)\b',
                    r'\b(?:I don\'t know|I\'m not sure|I can\'t be certain)\b',
                    r'\b(?:according to my knowledge|as far as I know)\b'
                ],
                'uncertainty_indicators': [
                    r'\b(?:might|could|may|possibly|likely)\b',
                    r'\b(?:it seems|it appears|it looks like)\b'
                ],
                'factual_indicators': [
                    r'\b(?:according to|based on|research shows|studies indicate)\b',
                    r'\b(?:the data shows|evidence suggests|findings indicate)\b'
                ]
            }
            
            self.logger.info("Response validation components initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing response validation: {e}")
    
    async def generate_response(
        self,
        query: str,
        context: List[Dict[str, Any]],
        conversation_history: List[Dict[str, str]] = None,
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Generate response with hallucination prevention and fact-checking
        
        Args:
            query: User query
            context: Retrieved context documents
            conversation_history: Previous conversation
            user_preferences: User-specific preferences
            
        Returns:
            Generated response with metadata and confidence scores
        """
        start_time = datetime.now()
        
        try:
            # Prepare context and prompt
            prepared_context = self._prepare_context(context)
            prompt = self._create_prompt(query, prepared_context, conversation_history)
            
            # Generate response with primary LLM
            response = await self._generate_with_llm(
                prompt, 
                self.config.primary_llm,
                user_preferences
            )
            
            # Apply fact-checking and validation
            if self.config.enable_fact_checking:
                response = await self._apply_fact_checking(response, context)
            
            # Apply response validation
            if self.config.enable_response_validation:
                response = await self._validate_response(response, context)
            
            # Calculate confidence score
            if self.config.enable_confidence_scoring:
                response['confidence_score'] = await self._calculate_confidence(
                    response, context, query
                )
            
            # Add source attribution
            if self.config.enable_source_attribution:
                response['sources'] = self._extract_sources(response, context)
            
            # Handle uncertainty
            if self.config.enable_uncertainty_handling:
                response = await self._handle_uncertainty(response, context)
            
            # Add metadata
            response['metadata'] = {
                'generation_time': (datetime.now() - start_time).total_seconds(),
                'model_used': response.get('model_used', self.config.primary_llm),
                'context_sources': len(context),
                'confidence_score': response.get('confidence_score', 0.0),
                'fact_checked': self.config.enable_fact_checking,
                'validated': self.config.enable_response_validation
            }
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return await self._generate_fallback_response(query, context)
    
    def _prepare_context(self, context: List[Dict[str, Any]]) -> str:
        """Prepare context for generation"""
        try:
            prepared_context = []
            
            for i, doc in enumerate(context):
                content = doc.get('content', '')
                metadata = doc.get('metadata', {})
                
                # Format context with source information
                context_item = f"Source {i+1}: {content}"
                if metadata:
                    context_item += f" (Metadata: {json.dumps(metadata)})"
                
                prepared_context.append(context_item)
            
            return "\n\n".join(prepared_context)
            
        except Exception as e:
            self.logger.error(f"Error preparing context: {e}")
            return ""
    
    def _create_prompt(
        self, 
        query: str, 
        context: str, 
        conversation_history: List[Dict[str, str]] = None
    ) -> str:
        """Create prompt with context and conversation history"""
        
        # Base prompt template
        prompt_template = """You are a helpful AI assistant that provides accurate, factual responses based on the given context. 

IMPORTANT INSTRUCTIONS:
1. Only use information from the provided context
2. If the context doesn't contain enough information, say so clearly
3. Do not make up or hallucinate information
4. Be transparent about uncertainty
5. Cite sources when possible
6. Maintain factual accuracy

Context:
{context}

Previous conversation:
{conversation_history}

User query: {query}

Please provide a helpful, accurate response based on the context above. If you cannot answer based on the provided context, please say so clearly."""

        # Prepare conversation history
        if conversation_history:
            history_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation_history[-5:]  # Last 5 messages
            ])
        else:
            history_text = "No previous conversation"
        
        # Format prompt
        prompt = prompt_template.format(
            context=context,
            conversation_history=history_text,
            query=query
        )
        
        return prompt
    
    async def _generate_with_llm(
        self, 
        prompt: str, 
        llm_name: str, 
        user_preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate response using specified LLM"""
        
        try:
            if llm_name == "openai" and "openai" in self.llm_clients:
                return await self._generate_with_openai(prompt, user_preferences)
            elif llm_name == "anthropic" and "anthropic" in self.llm_clients:
                return await self._generate_with_anthropic(prompt, user_preferences)
            elif llm_name == "cohere" and "cohere" in self.llm_clients:
                return await self._generate_with_cohere(prompt, user_preferences)
            elif llm_name == "local" and "local" in self.llm_clients:
                return await self._generate_with_local(prompt, user_preferences)
            else:
                # Try fallback LLMs
                for fallback_llm in (self.config.fallback_llms or []):
                    if fallback_llm in self.llm_clients:
                        return await self._generate_with_llm(prompt, fallback_llm, user_preferences)
                
                raise ValueError(f"LLM {llm_name} not available")
                
        except Exception as e:
            self.logger.error(f"Error generating with {llm_name}: {e}")
            raise
    
    async def _generate_with_openai(self, prompt: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using OpenAI"""
        try:
            response = await self.llm_clients["openai"].chat.completions.create(
                model=self.config.openai_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                top_p=self.config.top_p,
                frequency_penalty=self.config.frequency_penalty,
                presence_penalty=self.config.presence_penalty
            )
            
            return {
                'answer': response.choices[0].message.content,
                'model_used': 'openai',
                'usage': response.usage.dict() if hasattr(response.usage, 'dict') else {}
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI generation error: {e}")
            raise
    
    async def _generate_with_anthropic(self, prompt: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Anthropic"""
        try:
            response = await self.llm_clients["anthropic"].messages.create(
                model=self.config.anthropic_model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                'answer': response.content[0].text,
                'model_used': 'anthropic',
                'usage': response.usage.dict() if hasattr(response.usage, 'dict') else {}
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic generation error: {e}")
            raise
    
    async def _generate_with_cohere(self, prompt: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Cohere"""
        try:
            response = await self.llm_clients["cohere"].generate(
                model=self.config.cohere_model,
                prompt=prompt,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                p=self.config.top_p
            )
            
            return {
                'answer': response.generations[0].text,
                'model_used': 'cohere',
                'usage': {}
            }
            
        except Exception as e:
            self.logger.error(f"Cohere generation error: {e}")
            raise
    
    async def _generate_with_local(self, prompt: str, user_preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using local model"""
        try:
            client = self.llm_clients["local"]
            tokenizer = client["tokenizer"]
            model = client["model"]
            
            # Tokenize input
            inputs = tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            # Generate response
            with torch.no_grad():
                outputs = model.generate(
                    inputs,
                    max_length=inputs.shape[1] + self.config.max_tokens,
                    temperature=self.config.temperature,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            answer = response_text[len(prompt):].strip()
            
            return {
                'answer': answer,
                'model_used': 'local',
                'usage': {}
            }
            
        except Exception as e:
            self.logger.error(f"Local generation error: {e}")
            raise
    
    async def _apply_fact_checking(self, response: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply fact-checking to response"""
        try:
            answer = response.get('answer', '')
            fact_check_results = {
                'factual_claims': [],
                'uncertain_claims': [],
                'hallucination_indicators': [],
                'source_verification': []
            }
            
            # Extract factual claims
            factual_claims = self._extract_factual_claims(answer)
            fact_check_results['factual_claims'] = factual_claims
            
            # Check claims against context
            for claim in factual_claims:
                verification_result = await self._verify_claim_against_context(claim, context)
                fact_check_results['source_verification'].append(verification_result)
            
            # Check for hallucination indicators
            hallucination_indicators = self._detect_hallucination_indicators(answer)
            fact_check_results['hallucination_indicators'] = hallucination_indicators
            
            # Add fact-checking results to response
            response['fact_checking'] = fact_check_results
            
            return response
            
        except Exception as e:
            self.logger.error(f"Fact-checking error: {e}")
            return response
    
    def _extract_factual_claims(self, text: str) -> List[str]:
        """Extract factual claims from text"""
        claims = []
        
        # Extract sentences that contain factual information
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:  # Filter out very short sentences
                # Check if sentence contains factual indicators
                if any(indicator in sentence.lower() for indicator in [
                    'is', 'are', 'was', 'were', 'will be', 'has been', 'have been',
                    'according to', 'research shows', 'studies indicate', 'data shows'
                ]):
                    claims.append(sentence)
        
        return claims
    
    async def _verify_claim_against_context(self, claim: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Verify a claim against the provided context"""
        try:
            # Calculate similarity between claim and context
            claim_embedding = self.fact_checker.encode([claim])
            context_embeddings = self.fact_checker.encode([doc.get('content', '') for doc in context])
            
            # Find most similar context
            similarities = cosine_similarity(claim_embedding, context_embeddings)[0]
            max_similarity = max(similarities)
            best_match_idx = np.argmax(similarities)
            
            return {
                'claim': claim,
                'verified': max_similarity > 0.7,  # Threshold for verification
                'similarity_score': float(max_similarity),
                'best_match_source': best_match_idx,
                'context_snippet': context[best_match_idx].get('content', '')[:200] + '...'
            }
            
        except Exception as e:
            self.logger.error(f"Claim verification error: {e}")
            return {
                'claim': claim,
                'verified': False,
                'similarity_score': 0.0,
                'error': str(e)
            }
    
    def _detect_hallucination_indicators(self, text: str) -> List[str]:
        """Detect potential hallucination indicators in text"""
        indicators = []
        
        for pattern_name, pattern in self.fact_patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                indicators.extend([f"{pattern_name}: {match}" for match in matches])
        
        # Check for uncertainty indicators
        for pattern in self.validation_patterns['hallucination_indicators']:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                indicators.extend([f"uncertainty: {match}" for match in matches])
        
        return indicators
    
    async def _validate_response(self, response: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate response quality and accuracy"""
        try:
            answer = response.get('answer', '')
            validation_results = {
                'length_check': len(answer) > 10,
                'coherence_check': self._check_coherence(answer),
                'relevance_check': await self._check_relevance(answer, context),
                'completeness_check': self._check_completeness(answer),
                'bias_check': self._check_bias(answer)
            }
            
            # Calculate overall validation score
            validation_score = sum(validation_results.values()) / len(validation_results)
            response['validation_score'] = validation_score
            response['validation_results'] = validation_results
            
            return response
            
        except Exception as e:
            self.logger.error(f"Response validation error: {e}")
            return response
    
    def _check_coherence(self, text: str) -> bool:
        """Check if text is coherent and well-structured"""
        # Simple coherence check - can be enhanced
        sentences = re.split(r'[.!?]+', text)
        return len(sentences) > 1 and all(len(s.strip()) > 5 for s in sentences if s.strip())
    
    async def _check_relevance(self, answer: str, context: List[Dict[str, Any]]) -> bool:
        """Check if answer is relevant to the context"""
        try:
            if not context:
                return False
            
            # Calculate similarity between answer and context
            answer_embedding = self.fact_checker.encode([answer])
            context_embeddings = self.fact_checker.encode([doc.get('content', '') for doc in context])
            
            similarities = cosine_similarity(answer_embedding, context_embeddings)[0]
            max_similarity = max(similarities)
            
            return max_similarity > 0.3  # Threshold for relevance
            
        except Exception as e:
            self.logger.error(f"Relevance check error: {e}")
            return False
    
    def _check_completeness(self, text: str) -> bool:
        """Check if answer is complete and addresses the query"""
        # Simple completeness check
        return len(text) > 50 and text.strip().endswith(('.', '!', '?'))
    
    def _check_bias(self, text: str) -> bool:
        """Check for potential bias in the response"""
        # Simple bias detection - can be enhanced
        bias_indicators = [
            'always', 'never', 'all', 'none', 'everyone', 'nobody',
            'obviously', 'clearly', 'definitely', 'certainly'
        ]
        
        bias_count = sum(1 for indicator in bias_indicators if indicator.lower() in text.lower())
        return bias_count < 3  # Threshold for bias detection
    
    async def _calculate_confidence(
        self, 
        response: Dict[str, Any], 
        context: List[Dict[str, Any]], 
        query: str
    ) -> float:
        """Calculate confidence score for the response"""
        try:
            confidence_factors = []
            
            # Factor 1: Source coverage
            if context:
                source_coverage = min(len(context) / 3, 1.0)  # Normalize to 0-1
                confidence_factors.append(source_coverage)
            
            # Factor 2: Response validation score
            validation_score = response.get('validation_score', 0.5)
            confidence_factors.append(validation_score)
            
            # Factor 3: Fact-checking results
            fact_checking = response.get('fact_checking', {})
            if fact_checking.get('source_verification'):
                verified_claims = sum(1 for v in fact_checking['source_verification'] if v.get('verified', False))
                total_claims = len(fact_checking['source_verification'])
                if total_claims > 0:
                    fact_confidence = verified_claims / total_claims
                    confidence_factors.append(fact_confidence)
            
            # Factor 4: Response length and completeness
            answer_length = len(response.get('answer', ''))
            length_confidence = min(answer_length / 200, 1.0)  # Normalize to 0-1
            confidence_factors.append(length_confidence)
            
            # Calculate weighted average
            if confidence_factors:
                confidence_score = sum(confidence_factors) / len(confidence_factors)
            else:
                confidence_score = 0.5  # Default confidence
            
            return min(max(confidence_score, 0.0), 1.0)  # Clamp to 0-1
            
        except Exception as e:
            self.logger.error(f"Confidence calculation error: {e}")
            return 0.5  # Default confidence
    
    def _extract_sources(self, response: Dict[str, Any], context: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and format sources from context"""
        sources = []
        
        for i, doc in enumerate(context):
            source = {
                'index': i + 1,
                'content': doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', ''),
                'metadata': doc.get('metadata', {}),
                'relevance_score': doc.get('score', 0.0)
            }
            sources.append(source)
        
        return sources
    
    async def _handle_uncertainty(self, response: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle uncertainty in the response"""
        try:
            answer = response.get('answer', '')
            confidence_score = response.get('confidence_score', 0.5)
            
            # Add uncertainty handling based on confidence
            if confidence_score < self.config.confidence_threshold:
                uncertainty_note = "\n\nNote: I have limited confidence in this response. Please verify the information with additional sources."
                response['answer'] = answer + uncertainty_note
                response['uncertainty_handled'] = True
            else:
                response['uncertainty_handled'] = False
            
            return response
            
        except Exception as e:
            self.logger.error(f"Uncertainty handling error: {e}")
            return response
    
    async def _generate_fallback_response(self, query: str, context: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate fallback response when primary generation fails"""
        return {
            'answer': "I apologize, but I'm unable to generate a response at this time. Please try again later or rephrase your question.",
            'sources': [],
            'confidence_score': 0.0,
            'model_used': 'fallback',
            'error': 'Generation failed',
            'metadata': {
                'generation_time': 0.0,
                'fallback_used': True
            }
        }
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get generation system statistics"""
        return {
            'available_llms': list(self.llm_clients.keys()),
            'config': {
                'primary_llm': self.config.primary_llm,
                'fallback_llms': self.config.fallback_llms,
                'enable_fact_checking': self.config.enable_fact_checking,
                'enable_response_validation': self.config.enable_response_validation,
                'confidence_threshold': self.config.confidence_threshold
            }
        }

# Factory function for easy initialization
def create_modern_generation_system(config: Optional[GenerationConfig] = None) -> ModernGenerationSystem:
    """Create a modern generation system with default or custom configuration"""
    if config is None:
        config = GenerationConfig()
    
    return ModernGenerationSystem(config)
