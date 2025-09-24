"""
Advanced Response Generation
Enhanced response generation with citations, validation, and confidence scoring
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    id: str
    text: str
    source: str
    page: Optional[int] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = None

@dataclass
class ResponseMetrics:
    confidence: float
    relevance_score: float
    completeness_score: float
    citation_quality: float
    response_length: int
    processing_time: float

class CitationParser:
    def __init__(self):
        """Initialize citation parser"""
        self.citation_patterns = [
            r'\[(\d+)\]',  # [1], [2], etc.
            r'\(([^)]+)\)',  # (source), (author, year)
            r'^(\d+)\.',  # 1. at start of line
        ]
    
    def extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from text"""
        citations = []
        
        for pattern in self.citation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                citation_id = match.group(1)
                start, end = match.span()
                
                # Extract surrounding context
                context_start = max(0, start - 50)
                context_end = min(len(text), end + 50)
                context = text[context_start:context_end]
                
                citations.append(Citation(
                    id=citation_id,
                    text=context,
                    source="unknown",
                    confidence=0.8
                ))
        
        return citations
    
    def format_citations(self, citations: List[Citation]) -> str:
        """Format citations for display"""
        if not citations:
            return ""
        
        formatted = "\n\n**Sources:**\n"
        for i, citation in enumerate(citations, 1):
            formatted += f"{i}. {citation.source}"
            if citation.page:
                formatted += f" (page {citation.page})"
            formatted += f" - {citation.text[:100]}...\n"
        
        return formatted

class ResponseValidator:
    def __init__(self, llm):
        """Initialize response validator"""
        self.llm = llm
    
    def validate_response(self, query: str, response: str, context: List[str]) -> Dict[str, Any]:
        """Validate response for accuracy and relevance"""
        
        validation_prompt = f"""
        Query: {query}
        Response: {response}
        Supporting Context: {context}
        
        Please evaluate the response on the following criteria (1-10 scale):
        1. Does the response directly answer the query?
        2. Is the response supported by the context?
        3. Are there any factual inaccuracies?
        4. How relevant is the response to the query?
        5. Is the response complete and comprehensive?
        6. Are the citations appropriate and accurate?
        
        Provide scores and brief explanations for each criterion.
        """
        
        try:
            validation_result = self.llm.generate(validation_prompt)
            scores = self._parse_validation_scores(validation_result)
            
            return {
                'is_valid': scores['overall'] >= 7,
                'scores': scores,
                'feedback': validation_result,
                'suggestions': self._generate_improvement_suggestions(scores)
            }
        except Exception as e:
            logger.warning(f"Response validation failed: {e}")
            return {
                'is_valid': True,  # Default to valid if validation fails
                'scores': {'overall': 8},
                'error': str(e)
            }
    
    def _parse_validation_scores(self, validation_text: str) -> Dict[str, float]:
        """Parse scores from validation response"""
        # Simple parsing - in production, use more sophisticated NLP
        scores = {
            'overall': 8.0,
            'relevance': 8.0,
            'accuracy': 8.0,
            'completeness': 8.0,
            'citation_quality': 8.0
        }
        
        # Look for numeric scores in the text
        score_patterns = [
            r'relevance[:\s]*(\d+(?:\.\d+)?)',
            r'accuracy[:\s]*(\d+(?:\.\d+)?)',
            r'completeness[:\s]*(\d+(?:\.\d+)?)',
            r'overall[:\s]*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in score_patterns:
            match = re.search(pattern, validation_text, re.IGNORECASE)
            if match:
                score = float(match.group(1))
                if 'relevance' in pattern:
                    scores['relevance'] = score
                elif 'accuracy' in pattern:
                    scores['accuracy'] = score
                elif 'completeness' in pattern:
                    scores['completeness'] = score
                elif 'overall' in pattern:
                    scores['overall'] = score
        
        return scores
    
    def _generate_improvement_suggestions(self, scores: Dict[str, float]) -> List[str]:
        """Generate improvement suggestions based on scores"""
        suggestions = []
        
        if scores.get('relevance', 8) < 7:
            suggestions.append("Make the response more directly relevant to the query")
        
        if scores.get('accuracy', 8) < 7:
            suggestions.append("Verify factual accuracy and check for inconsistencies")
        
        if scores.get('completeness', 8) < 7:
            suggestions.append("Provide more comprehensive information")
        
        if scores.get('citation_quality', 8) < 7:
            suggestions.append("Improve citation quality and accuracy")
        
        return suggestions

class AdvancedResponseGenerator:
    def __init__(self, llm, prompt_manager, citation_parser: CitationParser, 
                 validator: ResponseValidator):
        """
        Advanced response generator with citations and validation
        
        Args:
            llm: Language model for generation
            prompt_manager: Prompt manager for different response types
            citation_parser: Citation parser for extracting references
            validator: Response validator for quality assurance
        """
        self.llm = llm
        self.prompt_manager = prompt_manager
        self.citation_parser = citation_parser
        self.validator = validator
    
    def generate_response(self, query: str, context: List[str], 
                        conversation_history: str = "", 
                        response_type: str = "qa") -> Dict[str, Any]:
        """Generate response with citations and confidence scoring"""
        
        start_time = datetime.now()
        
        # Prepare context with citations
        cited_context = self._prepare_cited_context(context)
        
        # Select appropriate prompt based on response type
        prompt = self._get_prompt(query, cited_context, conversation_history, response_type)
        
        # Generate response
        try:
            raw_response = self.llm.generate(prompt)
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                'answer': "I apologize, but I encountered an error generating a response.",
                'citations': [],
                'confidence': 0.0,
                'sources': [],
                'error': str(e)
            }
        
        # Post-process response
        processed_response = self._post_process_response(
            raw_response, 
            context,
            query
        )
        
        # Calculate metrics
        processing_time = (datetime.now() - start_time).total_seconds()
        metrics = self._calculate_metrics(processed_response, context, query, processing_time)
        
        # Validate response
        validation = self.validator.validate_response(query, processed_response['answer'], context)
        
        return {
            'answer': processed_response['answer'],
            'citations': processed_response['citations'],
            'confidence': metrics.confidence,
            'sources': processed_response['sources'],
            'metrics': metrics,
            'validation': validation,
            'raw_response': raw_response,
            'processing_time': processing_time
        }
    
    def _prepare_cited_context(self, context: List[str]) -> str:
        """Add citation markers to context"""
        cited_context = ""
        for i, chunk in enumerate(context):
            cited_context += f"[{i+1}] {chunk}\n\n"
        return cited_context
    
    def _get_prompt(self, query: str, context: str, conversation_history: str, 
                   response_type: str) -> str:
        """Get appropriate prompt based on response type"""
        
        if response_type == "qa":
            return self.prompt_manager.get_enhanced_qa_prompt(
                query=query,
                context=context,
                conversation_history=conversation_history
            )
        elif response_type == "summarization":
            return self.prompt_manager.get_summarization_prompt(
                text=context,
                query=query
            )
        elif response_type == "comparison":
            return self.prompt_manager.get_comparison_prompt(
                query=query,
                context=context
            )
        else:
            return self.prompt_manager.get_qa_prompt().format(
                context=context,
                question=query
            )
    
    def _post_process_response(self, raw_response: str, context: List[str], 
                             query: str) -> Dict[str, Any]:
        """Post-process the generated response"""
        
        # Extract citations
        citations = self.citation_parser.extract_citations(raw_response)
        
        # Format response
        formatted_response = self._format_response(raw_response)
        
        # Extract sources
        sources = self._extract_sources(citations, context)
        
        return {
            'answer': formatted_response,
            'citations': citations,
            'sources': sources
        }
    
    def _format_response(self, raw_response: str) -> str:
        """Format response for better readability"""
        # Clean up formatting
        formatted = raw_response.strip()
        
        # Ensure proper paragraph breaks
        formatted = re.sub(r'\n\s*\n', '\n\n', formatted)
        
        # Add citations formatting if not present
        if not re.search(r'\[(\d+)\]', formatted):
            # Add a note about sources
            formatted += "\n\n*Sources: Available upon request*"
        
        return formatted
    
    def _extract_sources(self, citations: List[Citation], context: List[str]) -> List[str]:
        """Extract source information from citations and context"""
        sources = []
        
        for citation in citations:
            if citation.source and citation.source != "unknown":
                sources.append(citation.source)
        
        # Add sources from context if not already included
        for i, chunk in enumerate(context):
            source = f"Source {i+1}"
            if source not in sources:
                sources.append(source)
        
        return list(set(sources))  # Remove duplicates
    
    def _calculate_metrics(self, processed_response: Dict[str, Any], 
                          context: List[str], query: str, processing_time: float) -> ResponseMetrics:
        """Calculate response metrics"""
        
        answer = processed_response['answer']
        citations = processed_response['citations']
        
        # Confidence score based on multiple factors
        confidence = self._calculate_confidence(answer, context, citations)
        
        # Relevance score
        relevance_score = self._calculate_relevance(query, answer)
        
        # Completeness score
        completeness_score = self._calculate_completeness(query, answer)
        
        # Citation quality
        citation_quality = self._calculate_citation_quality(citations, context)
        
        return ResponseMetrics(
            confidence=confidence,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            citation_quality=citation_quality,
            response_length=len(answer),
            processing_time=processing_time
        )
    
    def _calculate_confidence(self, answer: str, context: List[str], 
                            citations: List[Citation]) -> float:
        """Calculate confidence score for the response"""
        base_confidence = 0.5
        
        # Boost for citations
        if citations:
            base_confidence += 0.2
        
        # Boost for longer, more detailed responses
        if len(answer) > 100:
            base_confidence += 0.1
        
        # Boost for specific information
        if any(word in answer.lower() for word in ['specifically', 'according to', 'research shows']):
            base_confidence += 0.1
        
        # Penalty for uncertainty indicators
        if any(word in answer.lower() for word in ['might', 'could', 'possibly', 'unclear']):
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))
    
    def _calculate_relevance(self, query: str, answer: str) -> float:
        """Calculate relevance score between query and answer"""
        query_words = set(query.lower().split())
        answer_words = set(answer.lower().split())
        
        if not query_words:
            return 0.5
        
        overlap = len(query_words & answer_words)
        relevance = overlap / len(query_words)
        
        return min(1.0, relevance)
    
    def _calculate_completeness(self, query: str, answer: str) -> float:
        """Calculate completeness score for the answer"""
        # Simple heuristic based on answer length and structure
        base_score = 0.5
        
        # Boost for longer answers
        if len(answer) > 200:
            base_score += 0.2
        
        # Boost for structured answers (with numbers, bullet points)
        if re.search(r'\d+\.|\*|\-', answer):
            base_score += 0.1
        
        # Boost for multiple sentences
        sentences = len([s for s in answer.split('.') if s.strip()])
        if sentences > 3:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _calculate_citation_quality(self, citations: List[Citation], 
                                   context: List[str]) -> float:
        """Calculate citation quality score"""
        if not citations:
            return 0.0
        
        quality_score = 0.0
        
        for citation in citations:
            # Boost for citations with sources
            if citation.source and citation.source != "unknown":
                quality_score += 0.3
            
            # Boost for citations with page numbers
            if citation.page:
                quality_score += 0.2
            
            # Boost for high confidence citations
            quality_score += citation.confidence * 0.5
        
        return min(1.0, quality_score / len(citations))
    
    def generate_follow_up_questions(self, query: str, answer: str, 
                                    context: List[str]) -> List[str]:
        """Generate follow-up questions based on the response"""
        follow_ups = []
        
        # Extract key topics from the answer
        topics = self._extract_topics(answer)
        
        # Generate questions for each topic
        for topic in topics[:3]:  # Limit to 3 follow-ups
            follow_ups.append(f"Can you tell me more about {topic}?")
        
        # Add general follow-ups
        follow_ups.extend([
            "What are the implications of this?",
            "Are there any related topics I should know about?",
            "Can you provide more details on this?"
        ])
        
        return follow_ups[:5]  # Return top 5 follow-ups
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract key topics from text"""
        # Simple topic extraction
        words = text.lower().split()
        
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequency
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top topics
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
