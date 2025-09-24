"""
Self-Querying RAG Implementation
Latest 2024 technique for automatic query decomposition and structured data querying
"""

import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class QueryType(Enum):
    STRUCTURED_QUERY = "structured_query"
    NATURAL_LANGUAGE = "natural_language"
    HYBRID_QUERY = "hybrid_query"
    COMPLEX_ANALYTICAL = "complex_analytical"

class DataSourceType(Enum):
    VECTOR_DATABASE = "vector_database"
    RELATIONAL_DATABASE = "relational_database"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    DOCUMENT_STORE = "document_store"
    API_ENDPOINT = "api_endpoint"
    MIXED_SOURCES = "mixed_sources"

@dataclass
class QueryDecomposition:
    original_query: str
    query_type: QueryType
    decomposed_queries: List[str]
    structured_filters: Dict[str, Any]
    data_source_requirements: List[DataSourceType]
    execution_plan: List[Dict[str, Any]]
    confidence_score: float

@dataclass
class StructuredFilter:
    field: str
    operator: str  # 'eq', 'gt', 'lt', 'contains', 'between', 'in'
    value: Union[str, int, float, List]
    data_type: str
    source_metadata: Dict[str, Any]

@dataclass
class QueryExecutionResult:
    query_id: str
    data_source: DataSourceType
    results: List[Dict[str, Any]]
    execution_time: float
    result_count: int
    confidence: float
    metadata: Dict[str, Any]

class SelfQueryingRAGSystem:
    """
    Self-Querying RAG system that automatically decomposes queries and executes structured searches
    """
    
    def __init__(self, llm_client, vector_store, relational_db=None, knowledge_graph=None):
        self.llm_client = llm_client
        self.vector_store = vector_store
        self.relational_db = relational_db
        self.knowledge_graph = knowledge_graph
        
        # Query decomposition patterns
        self.decomposition_patterns = {
            'filter_extraction': [
                r'(?:find|get|show|list)\s+([^where]+?)\s+(?:where|with)\s+(.+)',
                r'(?:what|which|who)\s+(?:is|are)\s+([^?]+)\?',
                r'(?:how many|how much)\s+(.+)',
                r'(?:when|where)\s+(.+)'
            ],
            'aggregation_extraction': [
                r'(?:count|sum|average|max|min)\s+(.+)',
                r'(?:total|overall)\s+(.+)',
                r'(?:group by|grouped by)\s+(.+)'
            ],
            'comparison_extraction': [
                r'(?:compare|difference between|vs|versus)\s+(.+)',
                r'(?:better than|worse than|greater than|less than)\s+(.+)',
                r'(?:similar to|like)\s+(.+)'
            ]
        }
        
        # Data source mappings
        self.data_source_mappings = {
            'vector_database': ['similar', 'related', 'semantic', 'meaning'],
            'relational_database': ['count', 'sum', 'filter', 'where', 'group by'],
            'knowledge_graph': ['relationship', 'connected', 'entity', 'graph'],
            'document_store': ['document', 'text', 'content', 'paragraph']
        }
        
        # Query optimization rules
        self.optimization_rules = {
            'parallel_execution': True,
            'cache_intermediate_results': True,
            'adaptive_timeout': True,
            'result_merging': True
        }
    
    async def process_self_querying(self, query: str, user_context: Dict = None) -> Dict[str, Any]:
        """
        Process query using self-querying approach
        """
        logger.info(f"🤖 Processing self-querying for: '{query[:50]}...'")
        
        # Step 1: Analyze and decompose query
        query_decomposition = await self.decompose_query(query, user_context)
        
        logger.info(f"📊 Query decomposed into {len(query_decomposition.decomposed_queries)} sub-queries")
        
        # Step 2: Execute decomposed queries in parallel
        execution_results = await self.execute_decomposed_queries(query_decomposition)
        
        # Step 3: Merge and synthesize results
        synthesized_results = await self.synthesize_results(
            query_decomposition, execution_results
        )
        
        # Step 4: Generate final response
        final_response = await self.generate_self_querying_response(
            query, query_decomposition, synthesized_results
        )
        
        return {
            'query_decomposition': query_decomposition.__dict__,
            'execution_results': [result.__dict__ for result in execution_results],
            'synthesized_results': synthesized_results,
            'final_response': final_response,
            'processing_metadata': {
                'total_execution_time': sum(result.execution_time for result in execution_results),
                'queries_executed': len(execution_results),
                'data_sources_used': list(set(result.data_source for result in execution_results))
            }
        }
    
    async def decompose_query(self, query: str, user_context: Dict = None) -> QueryDecomposition:
        """
        Decompose complex query into structured components
        """
        # Analyze query type
        query_type = await self.classify_query_type(query)
        
        # Extract structured filters
        structured_filters = await self.extract_structured_filters(query)
        
        # Decompose into sub-queries
        decomposed_queries = await self.generate_sub_queries(query, structured_filters)
        
        # Determine data source requirements
        data_source_requirements = await self.determine_data_source_requirements(
            query, structured_filters
        )
        
        # Create execution plan
        execution_plan = await self.create_execution_plan(
            decomposed_queries, data_source_requirements
        )
        
        # Calculate confidence score
        confidence_score = await self.calculate_decomposition_confidence(
            query, decomposed_queries, structured_filters
        )
        
        return QueryDecomposition(
            original_query=query,
            query_type=query_type,
            decomposed_queries=decomposed_queries,
            structured_filters=structured_filters,
            data_source_requirements=data_source_requirements,
            execution_plan=execution_plan,
            confidence_score=confidence_score
        )
    
    async def classify_query_type(self, query: str) -> QueryType:
        """
        Classify the type of query for appropriate handling
        """
        query_lower = query.lower()
        
        # Check for structured query patterns
        structured_indicators = ['where', 'count', 'sum', 'group by', 'order by', 'having']
        if any(indicator in query_lower for indicator in structured_indicators):
            return QueryType.STRUCTURED_QUERY
        
        # Check for complex analytical patterns
        analytical_indicators = ['analyze', 'compare', 'relationship', 'correlation', 'trend']
        if any(indicator in query_lower for indicator in analytical_indicators):
            return QueryType.COMPLEX_ANALYTICAL
        
        # Check for hybrid patterns (mix of natural language and structured)
        if any(word in query_lower for word in ['find all', 'show me', 'list']) and \
           any(word in query_lower for word in ['that', 'where', 'with']):
            return QueryType.HYBRID_QUERY
        
        return QueryType.NATURAL_LANGUAGE
    
    async def extract_structured_filters(self, query: str) -> Dict[str, Any]:
        """
        Extract structured filters from natural language query
        """
        filters = {}
        query_lower = query.lower()
        
        # Extract date filters
        date_patterns = [
            r'(?:after|since|from)\s+(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},?\s+\d{4})',
            r'(?:before|until|to)\s+(\d{4}-\d{2}-\d{2}|\w+\s+\d{1,2},?\s+\d{4})',
            r'(\d{4}-\d{2}-\d{2})\s+(?:to|until)\s+(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if 'after' in match.group(0) or 'since' in match.group(0):
                    filters['date_from'] = match.group(1)
                elif 'before' in match.group(0) or 'until' in match.group(0):
                    filters['date_to'] = match.group(1)
                elif 'to' in match.group(0) and len(match.groups()) == 2:
                    filters['date_from'] = match.group(1)
                    filters['date_to'] = match.group(2)
        
        # Extract numeric filters
        numeric_patterns = [
            r'(?:greater than|more than|above)\s+(\d+(?:\.\d+)?)',
            r'(?:less than|below|under)\s+(\d+(?:\.\d+)?)',
            r'(?:between)\s+(\d+(?:\.\d+)?)\s+(?:and)\s+(\d+(?:\.\d+)?)',
            r'(?:equals?|exactly)\s+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in numeric_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if 'greater than' in match.group(0) or 'more than' in match.group(0):
                    filters['numeric_min'] = float(match.group(1))
                elif 'less than' in match.group(0) or 'below' in match.group(0):
                    filters['numeric_max'] = float(match.group(1))
                elif 'between' in match.group(0):
                    filters['numeric_min'] = float(match.group(1))
                    filters['numeric_max'] = float(match.group(2))
                elif 'equals' in match.group(0):
                    filters['numeric_equals'] = float(match.group(1))
        
        # Extract categorical filters
        categorical_patterns = [
            r'(?:category|type|status|class)\s+(?:is|equals?)\s+([^,\s]+)',
            r'(?:tagged|labeled|marked)\s+(?:as|with)\s+([^,\s]+)',
            r'(?:by|from|in)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in categorical_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if 'category' in match.group(0) or 'type' in match.group(0):
                    filters['category'] = match.group(1)
                elif 'tagged' in match.group(0) or 'labeled' in match.group(0):
                    filters['tags'] = match.group(1)
                else:
                    filters['source'] = match.group(1)
        
        # Extract text filters
        text_patterns = [
            r'(?:containing|with|including)\s+["\']([^"\']+)["\']',
            r'(?:about|regarding|concerning)\s+([^,.!?]+)',
            r'(?:related to|associated with)\s+([^,.!?]+)'
        ]
        
        for pattern in text_patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                if 'containing' in match.group(0):
                    filters['contains_text'] = match.group(1)
                elif 'about' in match.group(0):
                    filters['topic'] = match.group(1)
                elif 'related to' in match.group(0):
                    filters['related_to'] = match.group(1)
        
        return filters
    
    async def generate_sub_queries(self, original_query: str, filters: Dict[str, Any]) -> List[str]:
        """
        Generate sub-queries for different aspects of the original query
        """
        sub_queries = []
        
        # Base semantic query
        sub_queries.append(original_query)
        
        # Generate filter-specific queries
        if 'date_from' in filters or 'date_to' in filters:
            date_query = f"documents from {filters.get('date_from', 'beginning')} to {filters.get('date_to', 'now')}"
            if 'topic' in filters:
                date_query += f" about {filters['topic']}"
            sub_queries.append(date_query)
        
        if 'numeric_min' in filters or 'numeric_max' in filters:
            numeric_query = f"documents with values "
            if 'numeric_min' in filters and 'numeric_max' in filters:
                numeric_query += f"between {filters['numeric_min']} and {filters['numeric_max']}"
            elif 'numeric_min' in filters:
                numeric_query += f"greater than {filters['numeric_min']}"
            elif 'numeric_max' in filters:
                numeric_query += f"less than {filters['numeric_max']}"
            sub_queries.append(numeric_query)
        
        if 'category' in filters:
            category_query = f"documents in category {filters['category']}"
            if 'topic' in filters:
                category_query += f" about {filters['topic']}"
            sub_queries.append(category_query)
        
        if 'contains_text' in filters:
            text_query = f"documents containing '{filters['contains_text']}'"
            sub_queries.append(text_query)
        
        # Generate relationship queries
        if 'related_to' in filters:
            relationship_query = f"documents related to {filters['related_to']}"
            sub_queries.append(relationship_query)
        
        # Remove duplicates and return
        return list(set(sub_queries))
    
    async def determine_data_source_requirements(self, query: str, filters: Dict[str, Any]) -> List[DataSourceType]:
        """
        Determine which data sources are needed for the query
        """
        requirements = []
        query_lower = query.lower()
        
        # Check for vector database requirements
        vector_indicators = ['similar', 'related', 'semantic', 'meaning', 'about', 'concerning']
        if any(indicator in query_lower for indicator in vector_indicators):
            requirements.append(DataSourceType.VECTOR_DATABASE)
        
        # Check for relational database requirements
        relational_indicators = ['count', 'sum', 'average', 'max', 'min', 'group by', 'where', 'filter']
        if any(indicator in query_lower for indicator in relational_indicators):
            requirements.append(DataSourceType.RELATIONAL_DATABASE)
        
        # Check for knowledge graph requirements
        graph_indicators = ['relationship', 'connected', 'entity', 'graph', 'linked', 'associated']
        if any(indicator in query_lower for indicator in graph_indicators):
            requirements.append(DataSourceType.KNOWLEDGE_GRAPH)
        
        # Check for document store requirements
        document_indicators = ['document', 'text', 'content', 'paragraph', 'section']
        if any(indicator in query_lower for indicator in document_indicators):
            requirements.append(DataSourceType.DOCUMENT_STORE)
        
        # If multiple requirements, use mixed sources
        if len(requirements) > 1:
            requirements = [DataSourceType.MIXED_SOURCES]
        
        # Default to vector database if no specific requirements
        if not requirements:
            requirements = [DataSourceType.VECTOR_DATABASE]
        
        return requirements
    
    async def create_execution_plan(self, sub_queries: List[str], 
                                  data_source_requirements: List[DataSourceType]) -> List[Dict[str, Any]]:
        """
        Create execution plan for sub-queries
        """
        execution_plan = []
        
        for i, query in enumerate(sub_queries):
            # Determine data source for this query
            if i < len(data_source_requirements):
                data_source = data_source_requirements[i]
            else:
                data_source = data_source_requirements[0]
            
            # Create execution step
            execution_step = {
                'step_id': f"step_{i+1}",
                'query': query,
                'data_source': data_source,
                'priority': 1 if i == 0 else 2,  # First query has higher priority
                'timeout': 30,
                'retry_count': 2,
                'dependencies': [] if i == 0 else [f"step_{i}"]
            }
            
            execution_plan.append(execution_step)
        
        return execution_plan
    
    async def calculate_decomposition_confidence(self, original_query: str, 
                                               sub_queries: List[str], 
                                               filters: Dict[str, Any]) -> float:
        """
        Calculate confidence in the query decomposition
        """
        confidence = 0.5  # Base confidence
        
        # Boost confidence for clear filter extraction
        if filters:
            confidence += 0.2
        
        # Boost confidence for multiple sub-queries (indicates good decomposition)
        if len(sub_queries) > 1:
            confidence += 0.1
        
        # Boost confidence for structured query patterns
        structured_patterns = ['where', 'count', 'sum', 'group by', 'order by']
        if any(pattern in original_query.lower() for pattern in structured_patterns):
            confidence += 0.2
        
        return min(1.0, confidence)
    
    async def execute_decomposed_queries(self, decomposition: QueryDecomposition) -> List[QueryExecutionResult]:
        """
        Execute decomposed queries in parallel
        """
        execution_tasks = []
        
        for step in decomposition.execution_plan:
            task = self.execute_single_query(step)
            execution_tasks.append(task)
        
        # Execute all queries in parallel
        results = await asyncio.gather(*execution_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        execution_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Query execution failed for step {i}: {result}")
                # Create error result
                error_result = QueryExecutionResult(
                    query_id=f"step_{i+1}",
                    data_source=decomposition.execution_plan[i]['data_source'],
                    results=[],
                    execution_time=0,
                    result_count=0,
                    confidence=0.0,
                    metadata={'error': str(result)}
                )
                execution_results.append(error_result)
            else:
                execution_results.append(result)
        
        return execution_results
    
    async def execute_single_query(self, execution_step: Dict[str, Any]) -> QueryExecutionResult:
        """
        Execute a single query step
        """
        start_time = datetime.now()
        query = execution_step['query']
        data_source = execution_step['data_source']
        step_id = execution_step['step_id']
        
        try:
            # Route to appropriate data source
            if data_source == DataSourceType.VECTOR_DATABASE:
                results = await self.execute_vector_query(query)
            elif data_source == DataSourceType.RELATIONAL_DATABASE:
                results = await self.execute_relational_query(query)
            elif data_source == DataSourceType.KNOWLEDGE_GRAPH:
                results = await self.execute_graph_query(query)
            elif data_source == DataSourceType.DOCUMENT_STORE:
                results = await self.execute_document_query(query)
            else:
                # Mixed sources - try vector database first
                results = await self.execute_vector_query(query)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return QueryExecutionResult(
                query_id=step_id,
                data_source=data_source,
                results=results,
                execution_time=execution_time,
                result_count=len(results),
                confidence=0.8,  # Mock confidence
                metadata={'execution_step': execution_step}
            )
            
        except Exception as e:
            logger.error(f"Error executing query {step_id}: {e}")
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return QueryExecutionResult(
                query_id=step_id,
                data_source=data_source,
                results=[],
                execution_time=execution_time,
                result_count=0,
                confidence=0.0,
                metadata={'error': str(e), 'execution_step': execution_step}
            )
    
    async def execute_vector_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query against vector database
        """
        # Mock implementation
        return [
            {
                'content': f'Vector search result for: {query}',
                'score': 0.85,
                'source': 'vector_database',
                'metadata': {'query_type': 'semantic'}
            }
        ]
    
    async def execute_relational_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query against relational database
        """
        # Mock implementation
        return [
            {
                'content': f'Relational query result for: {query}',
                'count': 42,
                'source': 'relational_database',
                'metadata': {'query_type': 'structured'}
            }
        ]
    
    async def execute_graph_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query against knowledge graph
        """
        # Mock implementation
        return [
            {
                'content': f'Graph traversal result for: {query}',
                'entities': ['entity1', 'entity2'],
                'relationships': ['relates_to'],
                'source': 'knowledge_graph',
                'metadata': {'query_type': 'graph'}
            }
        ]
    
    async def execute_document_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute query against document store
        """
        # Mock implementation
        return [
            {
                'content': f'Document store result for: {query}',
                'document_id': 'doc_123',
                'source': 'document_store',
                'metadata': {'query_type': 'document'}
            }
        ]
    
    async def synthesize_results(self, decomposition: QueryDecomposition, 
                               execution_results: List[QueryExecutionResult]) -> Dict[str, Any]:
        """
        Synthesize results from multiple query executions
        """
        # Collect all results
        all_results = []
        result_metadata = {
            'total_queries_executed': len(execution_results),
            'successful_queries': len([r for r in execution_results if r.confidence > 0]),
            'total_execution_time': sum(r.execution_time for r in execution_results),
            'data_sources_used': list(set(r.data_source.value for r in execution_results))
        }
        
        for result in execution_results:
            if result.confidence > 0:
                all_results.extend(result.results)
        
        # Deduplicate results
        unique_results = self._deduplicate_results(all_results)
        
        # Rank and score results
        ranked_results = await self._rank_synthesized_results(unique_results, decomposition)
        
        return {
            'results': ranked_results,
            'metadata': result_metadata,
            'synthesis_confidence': await self._calculate_synthesis_confidence(execution_results)
        }
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate results based on content similarity
        """
        unique_results = []
        seen_hashes = set()
        
        for result in results:
            # Create content hash for deduplication
            content = result.get('content', '')
            content_hash = hash(content.lower().strip())
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_results.append(result)
        
        return unique_results
    
    async def _rank_synthesized_results(self, results: List[Dict[str, Any]], 
                                      decomposition: QueryDecomposition) -> List[Dict[str, Any]]:
        """
        Rank synthesized results based on relevance and quality
        """
        # Add ranking scores to results
        for result in results:
            # Base score from original result
            base_score = result.get('score', 0.5)
            
            # Boost score for matching original query intent
            query_match_boost = await self._calculate_query_match_boost(
                result, decomposition.original_query
            )
            
            # Boost score for result diversity
            diversity_boost = await self._calculate_diversity_boost(result, results)
            
            # Calculate final score
            final_score = base_score + query_match_boost + diversity_boost
            
            result['synthesis_score'] = min(1.0, final_score)
            result['ranking_factors'] = {
                'base_score': base_score,
                'query_match_boost': query_match_boost,
                'diversity_boost': diversity_boost
            }
        
        # Sort by synthesis score
        ranked_results = sorted(results, key=lambda x: x.get('synthesis_score', 0), reverse=True)
        
        return ranked_results
    
    async def _calculate_query_match_boost(self, result: Dict[str, Any], original_query: str) -> float:
        """
        Calculate boost score based on match with original query
        """
        # Simple keyword matching boost
        result_content = result.get('content', '').lower()
        query_words = set(original_query.lower().split())
        result_words = set(result_content.split())
        
        overlap = len(query_words & result_words)
        boost = overlap / len(query_words) if query_words else 0
        
        return boost * 0.2  # Max 20% boost
    
    async def _calculate_diversity_boost(self, result: Dict[str, Any], all_results: List[Dict[str, Any]]) -> float:
        """
        Calculate diversity boost for result variety
        """
        # Boost unique data sources
        source = result.get('source', '')
        source_count = sum(1 for r in all_results if r.get('source') == source)
        
        if source_count == 1:
            return 0.1  # 10% boost for unique sources
        elif source_count <= 3:
            return 0.05  # 5% boost for less common sources
        
        return 0.0
    
    async def _calculate_synthesis_confidence(self, execution_results: List[QueryExecutionResult]) -> float:
        """
        Calculate confidence in the synthesis process
        """
        if not execution_results:
            return 0.0
        
        # Average confidence of successful executions
        successful_results = [r for r in execution_results if r.confidence > 0]
        
        if not successful_results:
            return 0.0
        
        avg_confidence = sum(r.confidence for r in successful_results) / len(successful_results)
        
        # Boost confidence for multiple successful results
        diversity_boost = min(0.2, len(successful_results) * 0.05)
        
        return min(1.0, avg_confidence + diversity_boost)
    
    async def generate_self_querying_response(self, original_query: str, 
                                            decomposition: QueryDecomposition,
                                            synthesized_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate final response from self-querying results
        """
        results = synthesized_results['results']
        metadata = synthesized_results['metadata']
        
        # Create summary
        summary = f"Found {len(results)} relevant results from {metadata['successful_queries']} successful queries"
        
        # Extract top results
        top_results = results[:10]  # Top 10 results
        
        # Generate insights
        insights = await self._generate_query_insights(original_query, decomposition, results)
        
        return {
            'answer': f"Based on the self-querying analysis of '{original_query}', {summary}.",
            'results': top_results,
            'insights': insights,
            'query_analysis': {
                'original_query': original_query,
                'query_type': decomposition.query_type.value,
                'decomposition_confidence': decomposition.confidence_score,
                'sub_queries_executed': len(decomposition.decomposed_queries),
                'data_sources_used': metadata['data_sources_used']
            },
            'metadata': {
                'total_results': len(results),
                'execution_time': metadata['total_execution_time'],
                'synthesis_confidence': synthesized_results['synthesis_confidence']
            }
        }
    
    async def _generate_query_insights(self, original_query: str, 
                                     decomposition: QueryDecomposition,
                                     results: List[Dict[str, Any]]) -> List[str]:
        """
        Generate insights about the query and results
        """
        insights = []
        
        # Insight about query complexity
        if len(decomposition.decomposed_queries) > 2:
            insights.append(f"Complex query decomposed into {len(decomposition.decomposed_queries)} sub-queries")
        
        # Insight about data sources
        if len(set(r.get('source', '') for r in results)) > 1:
            insights.append("Results synthesized from multiple data sources")
        
        # Insight about result quality
        high_quality_results = [r for r in results if r.get('synthesis_score', 0) > 0.8]
        if high_quality_results:
            insights.append(f"{len(high_quality_results)} high-quality results found")
        
        # Insight about query type effectiveness
        if decomposition.query_type == QueryType.STRUCTURED_QUERY:
            insights.append("Structured query approach provided precise results")
        elif decomposition.query_type == QueryType.COMPLEX_ANALYTICAL:
            insights.append("Complex analytical query required multi-step processing")
        
        return insights
