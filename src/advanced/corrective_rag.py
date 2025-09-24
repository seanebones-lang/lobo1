"""
Corrective RAG (CRAG) Implementation
Latest 2024 technique for self-correcting retrieval with quality assessment
"""

import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class RetrievalQualityAssessment:
    relevance_score: float
    completeness_score: float
    accuracy_score: float
    diversity_score: float
    overall_quality: float
    needs_correction: bool
    correction_suggestions: List[str]

@dataclass
class CorrectiveAction:
    action_type: str  # 'refine_query', 'expand_search', 'switch_strategy', 'add_context'
    confidence: float
    parameters: Dict[str, Any]
    expected_improvement: float

class CorrectiveRAGSystem:
    """
    Corrective RAG system that self-assesses and corrects retrieval quality
    """
    
    def __init__(self, llm_client, vector_store, retrieval_orchestrator):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.retrieval_orchestrator = retrieval_orchestrator
        
        # Quality assessment thresholds
        self.quality_thresholds = {
            'relevance': 0.7,
            'completeness': 0.6,
            'accuracy': 0.8,
            'diversity': 0.5,
            'overall': 0.65
        }
        
        # Correction strategies
        self.correction_strategies = {
            'query_refinement': QueryRefinementStrategy(),
            'search_expansion': SearchExpansionStrategy(),
            'strategy_switching': StrategySwitchingStrategy(),
            'context_addition': ContextAdditionStrategy()
        }
    
    async def process_with_correction(self, query: str, user_context: Dict, 
                                    max_corrections: int = 3) -> Dict[str, Any]:
        """
        Process query with automatic correction and quality assessment
        """
        correction_history = []
        current_query = query
        best_result = None
        best_quality = 0.0
        
        for correction_round in range(max_corrections + 1):
            logger.info(f"🔄 Correction round {correction_round} for query: '{current_query[:50]}...'")
            
            # Step 1: Retrieve documents
            retrieval_result = await self.retrieval_orchestrator.retrieve(
                current_query, user_context
            )
            
            # Step 2: Assess retrieval quality
            quality_assessment = await self.assess_retrieval_quality(
                query, retrieval_result, user_context
            )
            
            logger.info(f"📊 Quality assessment: {quality_assessment.overall_quality:.3f}")
            
            # Step 3: Check if correction is needed
            if quality_assessment.overall_quality >= self.quality_thresholds['overall']:
                logger.info("✅ Quality threshold met, using current results")
                best_result = retrieval_result
                break
            
            # Step 4: Determine corrective action
            if correction_round < max_corrections:
                corrective_action = await self.determine_corrective_action(
                    query, retrieval_result, quality_assessment, correction_history
                )
                
                if corrective_action:
                    correction_history.append(corrective_action)
                    current_query = await self.apply_corrective_action(
                        corrective_action, current_query, retrieval_result, user_context
                    )
                    logger.info(f"🔧 Applied correction: {corrective_action.action_type}")
                else:
                    logger.info("❌ No corrective action found")
                    break
            else:
                logger.info("⚠️ Max corrections reached")
                break
        
        # Return best result with correction metadata
        return {
            'retrieval_result': best_result or retrieval_result,
            'quality_assessment': quality_assessment,
            'correction_history': correction_history,
            'corrections_applied': len(correction_history),
            'final_query': current_query,
            'improvement_achieved': quality_assessment.overall_quality - best_quality
        }
    
    async def assess_retrieval_quality(self, query: str, retrieval_result: Dict, 
                                     user_context: Dict) -> RetrievalQualityAssessment:
        """
        Assess the quality of retrieved documents using multiple criteria
        """
        documents = retrieval_result.get('documents', [])
        
        if not documents:
            return RetrievalQualityAssessment(
                relevance_score=0.0,
                completeness_score=0.0,
                accuracy_score=0.0,
                diversity_score=0.0,
                overall_quality=0.0,
                needs_correction=True,
                correction_suggestions=['No documents retrieved - expand search']
            )
        
        # Assess relevance
        relevance_score = await self._assess_relevance(query, documents)
        
        # Assess completeness
        completeness_score = await self._assess_completeness(query, documents)
        
        # Assess accuracy
        accuracy_score = await self._assess_accuracy(documents)
        
        # Assess diversity
        diversity_score = await self._assess_diversity(documents)
        
        # Calculate overall quality
        overall_quality = (
            relevance_score * 0.4 +
            completeness_score * 0.3 +
            accuracy_score * 0.2 +
            diversity_score * 0.1
        )
        
        # Determine if correction is needed
        needs_correction = overall_quality < self.quality_thresholds['overall']
        
        # Generate correction suggestions
        correction_suggestions = []
        if relevance_score < self.quality_thresholds['relevance']:
            correction_suggestions.append('Improve query relevance')
        if completeness_score < self.quality_thresholds['completeness']:
            correction_suggestions.append('Expand search scope')
        if accuracy_score < self.quality_thresholds['accuracy']:
            correction_suggestions.append('Filter low-quality sources')
        if diversity_score < self.quality_thresholds['diversity']:
            correction_suggestions.append('Increase result diversity')
        
        return RetrievalQualityAssessment(
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            accuracy_score=accuracy_score,
            diversity_score=diversity_score,
            overall_quality=overall_quality,
            needs_correction=needs_correction,
            correction_suggestions=correction_suggestions
        )
    
    async def _assess_relevance(self, query: str, documents: List[Dict]) -> float:
        """Assess relevance of documents to the query"""
        if not documents:
            return 0.0
        
        # Use LLM to assess relevance
        relevance_prompt = f"""
        Assess the relevance of these documents to the query: "{query}"
        
        Documents:
        {json.dumps([{'content': doc.get('content', '')[:200]} for doc in documents[:5]], indent=2)}
        
        Rate relevance on a scale of 0-1 for each document, then provide an average.
        Consider semantic similarity, topical alignment, and query intent matching.
        """
        
        try:
            response = await self.llm_client.generate(relevance_prompt)
            # Parse response to extract relevance score
            relevance_score = self._extract_score_from_response(response, 0.7)
        except Exception as e:
            logger.warning(f"Relevance assessment failed: {e}")
            # Fallback to simple keyword matching
            relevance_score = self._fallback_relevance_score(query, documents)
        
        return relevance_score
    
    async def _assess_completeness(self, query: str, documents: List[Dict]) -> float:
        """Assess completeness of retrieved information"""
        if not documents:
            return 0.0
        
        # Check if query aspects are covered
        query_aspects = await self._extract_query_aspects(query)
        covered_aspects = await self._check_aspect_coverage(query_aspects, documents)
        
        return covered_aspects / len(query_aspects) if query_aspects else 0.5
    
    async def _assess_accuracy(self, documents: List[Dict]) -> float:
        """Assess accuracy and reliability of documents"""
        if not documents:
            return 0.0
        
        accuracy_scores = []
        for doc in documents:
            # Check metadata for reliability indicators
            metadata = doc.get('metadata', {})
            source_quality = metadata.get('source_quality', 0.5)
            confidence = doc.get('confidence', 0.5)
            accuracy_scores.append((source_quality + confidence) / 2)
        
        return np.mean(accuracy_scores) if accuracy_scores else 0.5
    
    async def _assess_diversity(self, documents: List[Dict]) -> float:
        """Assess diversity of retrieved documents"""
        if len(documents) <= 1:
            return 0.0
        
        # Calculate content diversity using embeddings
        contents = [doc.get('content', '') for doc in documents]
        diversity_score = await self._calculate_content_diversity(contents)
        
        return diversity_score
    
    async def _extract_query_aspects(self, query: str) -> List[str]:
        """Extract different aspects from the query"""
        aspect_prompt = f"""
        Extract the key aspects or sub-questions from this query: "{query}"
        
        List each aspect as a separate item. For example:
        - "What is X?"
        - "How does X work?"
        - "What are the benefits of X?"
        """
        
        try:
            response = await self.llm_client.generate(aspect_prompt)
            aspects = self._parse_aspects_from_response(response)
        except:
            # Fallback to simple parsing
            aspects = [query]
        
        return aspects
    
    async def _check_aspect_coverage(self, aspects: List[str], documents: List[Dict]) -> int:
        """Check how many aspects are covered by the documents"""
        covered_count = 0
        
        for aspect in aspects:
            coverage_prompt = f"""
            Does this aspect: "{aspect}" appear to be covered in these documents?
            
            Documents:
            {json.dumps([{'content': doc.get('content', '')[:100]} for doc in documents], indent=2)}
            
            Answer yes or no.
            """
            
            try:
                response = await self.llm_client.generate(coverage_prompt)
                if 'yes' in response.lower():
                    covered_count += 1
            except:
                # Assume covered if we can't assess
                covered_count += 1
        
        return covered_count
    
    async def _calculate_content_diversity(self, contents: List[str]) -> float:
        """Calculate diversity of content using embeddings"""
        if len(contents) <= 1:
            return 0.0
        
        # Generate embeddings for all contents
        embeddings = []
        for content in contents:
            embedding = await self._get_content_embedding(content)
            embeddings.append(embedding)
        
        # Calculate pairwise cosine similarities
        similarities = []
        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
                )
                similarities.append(similarity)
        
        # Diversity is inverse of average similarity
        avg_similarity = np.mean(similarities) if similarities else 0.5
        diversity = 1.0 - avg_similarity
        
        return max(0.0, min(1.0, diversity))
    
    async def _get_content_embedding(self, content: str) -> np.ndarray:
        """Get embedding for content"""
        # Mock implementation - in practice, use actual embedding service
        return np.random.rand(384)  # 384-dimensional embedding
    
    async def determine_corrective_action(self, original_query: str, retrieval_result: Dict,
                                        quality_assessment: RetrievalQualityAssessment,
                                        correction_history: List[CorrectiveAction]) -> Optional[CorrectiveAction]:
        """Determine the best corrective action to take"""
        
        # Analyze quality gaps
        quality_gaps = {
            'relevance': self.quality_thresholds['relevance'] - quality_assessment.relevance_score,
            'completeness': self.quality_thresholds['completeness'] - quality_assessment.completeness_score,
            'diversity': self.quality_thresholds['diversity'] - quality_assessment.diversity_score
        }
        
        # Find the largest quality gap
        max_gap_aspect = max(quality_gaps.items(), key=lambda x: x[1])[0]
        max_gap = max_gap_aspect
        
        # Avoid repeating the same correction
        used_actions = [action.action_type for action in correction_history]
        
        # Determine corrective action based on quality gaps
        if max_gap == 'relevance' and 'query_refinement' not in used_actions:
            return CorrectiveAction(
                action_type='query_refinement',
                confidence=0.8,
                parameters={'focus': 'relevance', 'technique': 'semantic_expansion'},
                expected_improvement=0.2
            )
        elif max_gap == 'completeness' and 'search_expansion' not in used_actions:
            return CorrectiveAction(
                action_type='search_expansion',
                confidence=0.7,
                parameters={'expansion_factor': 1.5, 'include_synonyms': True},
                expected_improvement=0.15
            )
        elif max_gap == 'diversity' and 'strategy_switching' not in used_actions:
            return CorrectiveAction(
                action_type='strategy_switching',
                confidence=0.6,
                parameters={'new_strategies': ['semantic_search', 'graph_based']},
                expected_improvement=0.1
            )
        elif 'context_addition' not in used_actions:
            return CorrectiveAction(
                action_type='context_addition',
                confidence=0.5,
                parameters={'add_conversation_context': True, 'add_user_profile': True},
                expected_improvement=0.1
            )
        
        return None
    
    async def apply_corrective_action(self, action: CorrectiveAction, current_query: str,
                                   retrieval_result: Dict, user_context: Dict) -> str:
        """Apply the corrective action to improve the query"""
        
        strategy = self.correction_strategies.get(action.action_type)
        if strategy:
            return await strategy.apply(current_query, action.parameters, user_context)
        
        return current_query
    
    def _extract_score_from_response(self, response: str, default: float) -> float:
        """Extract numerical score from LLM response"""
        import re
        
        # Look for numerical scores
        numbers = re.findall(r'\b(0\.\d+|\d+\.\d+|\d+)\b', response)
        if numbers:
            return float(numbers[-1])  # Take the last number found
        
        return default
    
    def _parse_aspects_from_response(self, response: str) -> List[str]:
        """Parse aspects from LLM response"""
        lines = response.strip().split('\n')
        aspects = []
        
        for line in lines:
            line = line.strip()
            if line and ('-' in line or line.startswith('•')):
                aspect = line.split('-', 1)[-1].strip() if '-' in line else line[1:].strip()
                if aspect:
                    aspects.append(aspect)
        
        return aspects if aspects else ['General query']
    
    def _fallback_relevance_score(self, query: str, documents: List[Dict]) -> float:
        """Fallback relevance scoring using keyword matching"""
        query_words = set(query.lower().split())
        relevance_scores = []
        
        for doc in documents:
            doc_content = doc.get('content', '').lower()
            doc_words = set(doc_content.split())
            
            # Calculate Jaccard similarity
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            
            if union > 0:
                relevance_scores.append(intersection / union)
            else:
                relevance_scores.append(0.0)
        
        return np.mean(relevance_scores) if relevance_scores else 0.0

# Correction Strategy Classes
class QueryRefinementStrategy:
    async def apply(self, query: str, parameters: Dict, user_context: Dict) -> str:
        """Refine the query for better relevance"""
        # Mock implementation
        return f"{query} (refined for relevance)"

class SearchExpansionStrategy:
    async def apply(self, query: str, parameters: Dict, user_context: Dict) -> str:
        """Expand the search for better completeness"""
        # Mock implementation
        return f"{query} with expanded scope"

class StrategySwitchingStrategy:
    async def apply(self, query: str, parameters: Dict, user_context: Dict) -> str:
        """Switch retrieval strategies"""
        # This would modify the retrieval orchestrator
        return query

class ContextAdditionStrategy:
    async def apply(self, query: str, parameters: Dict, user_context: Dict) -> str:
        """Add context to improve retrieval"""
        context_info = user_context.get('conversation_history', [])
        if context_info:
            return f"{query} (with conversation context)"
        return query
