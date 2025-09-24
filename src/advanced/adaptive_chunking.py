"""
Adaptive Chunking Strategy
Latest 2024 technique for intelligent document chunking based on content structure and semantics
"""

import asyncio
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import logging
from datetime import datetime
import re
import json
from enum import Enum

logger = logging.getLogger(__name__)

class ContentType(Enum):
    TECHNICAL_DOCUMENTATION = "technical_documentation"
    LEGAL_DOCUMENT = "legal_document"
    ACADEMIC_PAPER = "academic_paper"
    CONVERSATION = "conversation"
    CODE = "code"
    STRUCTURED_DATA = "structured_data"
    GENERAL_TEXT = "general_text"

class ChunkingStrategy(Enum):
    SEMANTIC_CHUNKING = "semantic_chunking"
    RECURSIVE_CHUNKING = "recursive_chunking"
    FIXED_SIZE_CHUNKING = "fixed_size_chunking"
    ADAPTIVE_CHUNKING = "adaptive_chunking"
    SENTENCE_CHUNKING = "sentence_chunking"
    PARAGRAPH_CHUNKING = "paragraph_chunking"
    TOPIC_CHUNKING = "topic_chunking"

@dataclass
class ChunkMetadata:
    chunk_id: str
    content_type: ContentType
    chunking_strategy: ChunkingStrategy
    chunk_size: int
    overlap_size: int
    semantic_coherence: float
    topic_consistency: float
    structural_integrity: float
    retrieval_optimized: bool
    parent_document_id: str
    position_in_document: int
    sibling_chunks: List[str]
    semantic_embedding: Optional[np.ndarray] = None

@dataclass
class DocumentAnalysis:
    content_type: ContentType
    structure_type: str
    language: str
    complexity_score: float
    topic_density: float
    semantic_coherence: float
    optimal_chunk_size: int
    recommended_strategies: List[ChunkingStrategy]
    structural_elements: Dict[str, List[Tuple[int, int]]]  # element_type: [(start, end), ...]

class AdaptiveChunkingEngine:
    """
    Advanced adaptive chunking engine that analyzes documents and applies optimal chunking strategies
    """
    
    def __init__(self, llm_client, embedding_client):
        self.llm_client = llm_client
        self.embedding_client = embedding_client
        
        # Chunking strategy configurations
        self.strategy_configs = {
            ChunkingStrategy.SEMANTIC_CHUNKING: {
                'max_chunk_size': 1000,
                'min_chunk_size': 200,
                'overlap_size': 100,
                'coherence_threshold': 0.7
            },
            ChunkingStrategy.RECURSIVE_CHUNKING: {
                'max_chunk_size': 2000,
                'min_chunk_size': 100,
                'overlap_size': 50,
                'recursion_levels': 3
            },
            ChunkingStrategy.FIXED_SIZE_CHUNKING: {
                'chunk_size': 512,
                'overlap_size': 50,
                'preserve_sentences': True
            },
            ChunkingStrategy.ADAPTIVE_CHUNKING: {
                'dynamic_size': True,
                'content_aware': True,
                'semantic_boundaries': True
            },
            ChunkingStrategy.SENTENCE_CHUNKING: {
                'max_sentences': 5,
                'min_sentences': 2,
                'overlap_sentences': 1
            },
            ChunkingStrategy.PARAGRAPH_CHUNKING: {
                'max_paragraphs': 3,
                'min_paragraphs': 1,
                'overlap_paragraphs': 1
            },
            ChunkingStrategy.TOPIC_CHUNKING: {
                'topic_threshold': 0.8,
                'min_chunk_size': 150,
                'max_chunk_size': 800
            }
        }
        
        # Content type specific configurations
        self.content_type_configs = {
            ContentType.TECHNICAL_DOCUMENTATION: {
                'preferred_strategies': [ChunkingStrategy.SEMANTIC_CHUNKING, ChunkingStrategy.TOPIC_CHUNKING],
                'chunk_size_range': (300, 800),
                'preserve_code_blocks': True,
                'preserve_headers': True
            },
            ContentType.LEGAL_DOCUMENT: {
                'preferred_strategies': [ChunkingStrategy.PARAGRAPH_CHUNKING, ChunkingStrategy.SEMANTIC_CHUNKING],
                'chunk_size_range': (400, 1200),
                'preserve_sections': True,
                'preserve_citations': True
            },
            ContentType.ACADEMIC_PAPER: {
                'preferred_strategies': [ChunkingStrategy.TOPIC_CHUNKING, ChunkingStrategy.SEMANTIC_CHUNKING],
                'chunk_size_range': (500, 1000),
                'preserve_abstract': True,
                'preserve_citations': True
            },
            ContentType.CONVERSATION: {
                'preferred_strategies': [ChunkingStrategy.SENTENCE_CHUNKING, ChunkingStrategy.ADAPTIVE_CHUNKING],
                'chunk_size_range': (200, 600),
                'preserve_speakers': True,
                'preserve_turn_boundaries': True
            },
            ContentType.CODE: {
                'preferred_strategies': [ChunkingStrategy.SEMANTIC_CHUNKING, ChunkingStrategy.FIXED_SIZE_CHUNKING],
                'chunk_size_range': (300, 800),
                'preserve_functions': True,
                'preserve_imports': True
            },
            ContentType.GENERAL_TEXT: {
                'preferred_strategies': [ChunkingStrategy.SEMANTIC_CHUNKING, ChunkingStrategy.ADAPTIVE_CHUNKING],
                'chunk_size_range': (300, 700),
                'preserve_paragraphs': True
            }
        }
    
    async def chunk_document(self, document: Dict[str, Any], 
                           user_preferences: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Intelligently chunk a document using adaptive strategies
        """
        content = document.get('content', '')
        doc_id = document.get('doc_id', 'unknown')
        
        if not content.strip():
            return []
        
        logger.info(f"📄 Analyzing document {doc_id} for adaptive chunking")
        
        # Step 1: Analyze document structure and content type
        document_analysis = await self.analyze_document(content)
        
        # Step 2: Select optimal chunking strategy
        selected_strategy = await self.select_optimal_strategy(
            document_analysis, user_preferences
        )
        
        logger.info(f"🎯 Selected chunking strategy: {selected_strategy.value}")
        
        # Step 3: Apply chunking strategy
        chunks = await self.apply_chunking_strategy(
            content, document_analysis, selected_strategy, doc_id
        )
        
        # Step 4: Optimize chunks for retrieval
        optimized_chunks = await self.optimize_chunks_for_retrieval(
            chunks, document_analysis
        )
        
        # Step 5: Generate chunk metadata
        final_chunks = await self.generate_chunk_metadata(
            optimized_chunks, document_analysis, selected_strategy, doc_id
        )
        
        logger.info(f"✅ Generated {len(final_chunks)} optimized chunks")
        
        return final_chunks
    
    async def analyze_document(self, content: str) -> DocumentAnalysis:
        """
        Analyze document to determine optimal chunking approach
        """
        # Detect content type
        content_type = await self.detect_content_type(content)
        
        # Analyze document structure
        structure_analysis = await self.analyze_document_structure(content)
        
        # Calculate complexity and coherence metrics
        complexity_score = await self.calculate_complexity_score(content)
        topic_density = await self.calculate_topic_density(content)
        semantic_coherence = await self.calculate_semantic_coherence(content)
        
        # Determine optimal chunk size
        optimal_chunk_size = await self.determine_optimal_chunk_size(
            content_type, complexity_score, topic_density
        )
        
        # Recommend chunking strategies
        recommended_strategies = await self.recommend_chunking_strategies(
            content_type, structure_analysis, complexity_score
        )
        
        return DocumentAnalysis(
            content_type=content_type,
            structure_type=structure_analysis['type'],
            language=structure_analysis['language'],
            complexity_score=complexity_score,
            topic_density=topic_density,
            semantic_coherence=semantic_coherence,
            optimal_chunk_size=optimal_chunk_size,
            recommended_strategies=recommended_strategies,
            structural_elements=structure_analysis['elements']
        )
    
    async def detect_content_type(self, content: str) -> ContentType:
        """
        Detect the type of content for optimal chunking
        """
        content_lower = content.lower()
        
        # Technical documentation indicators
        if any(indicator in content_lower for indicator in [
            'api', 'function', 'method', 'parameter', 'returns', 'example',
            'installation', 'configuration', 'usage', 'documentation'
        ]):
            return ContentType.TECHNICAL_DOCUMENTATION
        
        # Legal document indicators
        if any(indicator in content_lower for indicator in [
            'whereas', 'therefore', 'hereby', 'agreement', 'contract',
            'terms and conditions', 'liability', 'jurisdiction'
        ]):
            return ContentType.LEGAL_DOCUMENT
        
        # Academic paper indicators
        if any(indicator in content_lower for indicator in [
            'abstract', 'introduction', 'methodology', 'results', 'conclusion',
            'references', 'bibliography', 'doi:', 'et al.'
        ]):
            return ContentType.ACADEMIC_PAPER
        
        # Conversation indicators
        if any(indicator in content_lower for indicator in [
            'speaker:', 'user:', 'assistant:', 'q:', 'a:', 'said:', 'asked:'
        ]) or re.search(r'^[A-Z][a-z]+:', content, re.MULTILINE):
            return ContentType.CONVERSATION
        
        # Code indicators
        if any(indicator in content_lower for indicator in [
            'def ', 'function ', 'class ', 'import ', 'from ', 'return ',
            'if __name__', 'public class', 'private ', 'public '
        ]) or re.search(r'```[\s\S]*?```', content):
            return ContentType.CODE
        
        # Structured data indicators
        if re.search(r'^\s*[{}[\],]', content, re.MULTILINE) or \
           re.search(r'^\s*\w+\s*[:=]\s*', content, re.MULTILINE):
            return ContentType.STRUCTURED_DATA
        
        return ContentType.GENERAL_TEXT
    
    async def analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """
        Analyze document structure to identify boundaries and elements
        """
        structure = {
            'type': 'linear',
            'language': 'en',
            'elements': {}
        }
        
        # Detect headers
        headers = []
        for match in re.finditer(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE):
            level = len(match.group(1))
            text = match.group(2).strip()
            headers.append((match.start(), match.end(), level, text))
        structure['elements']['headers'] = headers
        
        # Detect paragraphs
        paragraphs = []
        for match in re.finditer(r'\n\s*\n', content):
            paragraphs.append((match.start(), match.end()))
        structure['elements']['paragraphs'] = paragraphs
        
        # Detect sentences
        sentences = []
        for match in re.finditer(r'[.!?]+\s+', content):
            sentences.append((match.start(), match.end()))
        structure['elements']['sentences'] = sentences
        
        # Detect lists
        lists = []
        for match in re.finditer(r'^\s*[-*+]\s+.+$', content, re.MULTILINE):
            lists.append((match.start(), match.end()))
        structure['elements']['lists'] = lists
        
        # Detect code blocks
        code_blocks = []
        for match in re.finditer(r'```[\s\S]*?```', content):
            code_blocks.append((match.start(), match.end()))
        structure['elements']['code_blocks'] = code_blocks
        
        # Determine structure type
        if headers:
            structure['type'] = 'hierarchical'
        elif len(paragraphs) > 10:
            structure['type'] = 'paragraph_based'
        else:
            structure['type'] = 'linear'
        
        return structure
    
    async def calculate_complexity_score(self, content: str) -> float:
        """
        Calculate document complexity score
        """
        # Average sentence length
        sentences = re.split(r'[.!?]+', content)
        avg_sentence_length = np.mean([len(s.split()) for s in sentences if s.strip()])
        
        # Average word length
        words = content.split()
        avg_word_length = np.mean([len(w) for w in words if w.isalpha()])
        
        # Technical term density
        technical_terms = re.findall(r'\b[A-Z]{2,}\b|\b[a-z]+_[a-z]+\b', content)
        technical_density = len(technical_terms) / len(words) if words else 0
        
        # Syntactic complexity (parentheses, semicolons, etc.)
        complex_punctuation = len(re.findall(r'[;:(){}[\]"]', content))
        punctuation_density = complex_punctuation / len(words) if words else 0
        
        # Combine metrics
        complexity = (
            min(1.0, avg_sentence_length / 20) * 0.3 +
            min(1.0, avg_word_length / 8) * 0.2 +
            min(1.0, technical_density * 10) * 0.3 +
            min(1.0, punctuation_density * 5) * 0.2
        )
        
        return complexity
    
    async def calculate_topic_density(self, content: str) -> float:
        """
        Calculate topic density (how many different topics are covered)
        """
        # Simple keyword-based topic detection
        words = content.lower().split()
        
        # Topic categories
        topics = {
            'technology': ['software', 'hardware', 'computer', 'system', 'data', 'algorithm'],
            'business': ['company', 'market', 'revenue', 'customer', 'product', 'service'],
            'science': ['research', 'study', 'experiment', 'theory', 'hypothesis', 'analysis'],
            'education': ['learn', 'teach', 'student', 'course', 'knowledge', 'skill'],
            'health': ['medical', 'health', 'patient', 'treatment', 'disease', 'medicine']
        }
        
        topic_counts = {topic: 0 for topic in topics}
        
        for word in words:
            for topic, keywords in topics.items():
                if word in keywords:
                    topic_counts[topic] += 1
        
        # Calculate diversity
        total_topics = sum(topic_counts.values())
        if total_topics == 0:
            return 0.0
        
        topic_diversity = len([count for count in topic_counts.values() if count > 0]) / len(topics)
        return topic_diversity
    
    async def calculate_semantic_coherence(self, content: str) -> float:
        """
        Calculate semantic coherence of the document
        """
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        if len(sentences) < 2:
            return 1.0
        
        # Mock semantic coherence calculation
        # In practice, use embeddings to calculate similarity between adjacent sentences
        coherence_scores = []
        for i in range(len(sentences) - 1):
            # Simple word overlap as proxy for semantic similarity
            words1 = set(sentences[i].lower().split())
            words2 = set(sentences[i + 1].lower().split())
            
            if words1 and words2:
                overlap = len(words1 & words2) / len(words1 | words2)
                coherence_scores.append(overlap)
        
        return np.mean(coherence_scores) if coherence_scores else 0.5
    
    async def determine_optimal_chunk_size(self, content_type: ContentType, 
                                         complexity_score: float, 
                                         topic_density: float) -> int:
        """
        Determine optimal chunk size based on content characteristics
        """
        base_sizes = {
            ContentType.TECHNICAL_DOCUMENTATION: 600,
            ContentType.LEGAL_DOCUMENT: 800,
            ContentType.ACADEMIC_PAPER: 700,
            ContentType.CONVERSATION: 400,
            ContentType.CODE: 500,
            ContentType.STRUCTURED_DATA: 300,
            ContentType.GENERAL_TEXT: 500
        }
        
        base_size = base_sizes.get(content_type, 500)
        
        # Adjust for complexity
        complexity_factor = 1.0 + (complexity_score - 0.5) * 0.4
        base_size = int(base_size * complexity_factor)
        
        # Adjust for topic density
        density_factor = 1.0 + (topic_density - 0.5) * 0.2
        base_size = int(base_size * density_factor)
        
        # Ensure reasonable bounds
        return max(200, min(1200, base_size))
    
    async def recommend_chunking_strategies(self, content_type: ContentType, 
                                          structure_analysis: Dict,
                                          complexity_score: float) -> List[ChunkingStrategy]:
        """
        Recommend optimal chunking strategies based on analysis
        """
        # Get content-type specific recommendations
        content_config = self.content_type_configs.get(content_type, {})
        preferred_strategies = content_config.get('preferred_strategies', [ChunkingStrategy.SEMANTIC_CHUNKING])
        
        # Adjust based on structure
        if structure_analysis['type'] == 'hierarchical':
            preferred_strategies.append(ChunkingStrategy.TOPIC_CHUNKING)
        elif structure_analysis['type'] == 'paragraph_based':
            preferred_strategies.append(ChunkingStrategy.PARAGRAPH_CHUNKING)
        
        # Adjust based on complexity
        if complexity_score > 0.7:
            preferred_strategies.append(ChunkingStrategy.SEMANTIC_CHUNKING)
        else:
            preferred_strategies.append(ChunkingStrategy.ADAPTIVE_CHUNKING)
        
        # Remove duplicates and return top 3
        unique_strategies = list(dict.fromkeys(preferred_strategies))
        return unique_strategies[:3]
    
    async def select_optimal_strategy(self, document_analysis: DocumentAnalysis,
                                    user_preferences: Dict = None) -> ChunkingStrategy:
        """
        Select the optimal chunking strategy
        """
        if user_preferences and 'preferred_strategy' in user_preferences:
            return ChunkingStrategy(user_preferences['preferred_strategy'])
        
        # Use the first recommended strategy
        return document_analysis.recommended_strategies[0]
    
    async def apply_chunking_strategy(self, content: str, document_analysis: DocumentAnalysis,
                                    strategy: ChunkingStrategy, doc_id: str) -> List[Dict[str, Any]]:
        """
        Apply the selected chunking strategy
        """
        if strategy == ChunkingStrategy.SEMANTIC_CHUNKING:
            return await self.semantic_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.RECURSIVE_CHUNKING:
            return await self.recursive_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.FIXED_SIZE_CHUNKING:
            return await self.fixed_size_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.ADAPTIVE_CHUNKING:
            return await self.adaptive_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.SENTENCE_CHUNKING:
            return await self.sentence_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.PARAGRAPH_CHUNKING:
            return await self.paragraph_chunking(content, document_analysis, doc_id)
        elif strategy == ChunkingStrategy.TOPIC_CHUNKING:
            return await self.topic_chunking(content, document_analysis, doc_id)
        else:
            # Default to semantic chunking
            return await self.semantic_chunking(content, document_analysis, doc_id)
    
    async def semantic_chunking(self, content: str, analysis: DocumentAnalysis, 
                              doc_id: str) -> List[Dict[str, Any]]:
        """
        Semantic chunking based on content coherence
        """
        config = self.strategy_configs[ChunkingStrategy.SEMANTIC_CHUNKING]
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence.split())
            
            # Check if adding this sentence would exceed max size
            if current_size + sentence_size > config['max_chunk_size'] and current_chunk:
                # Create chunk
                chunk_content = ' '.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'start_sentence': i - len(current_chunk),
                    'end_sentence': i - 1,
                    'size': current_size
                })
                
                # Start new chunk with overlap
                overlap_size = min(config['overlap_size'], current_size)
                if overlap_size > 0 and len(current_chunk) > 1:
                    # Keep last few sentences for overlap
                    overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                    current_chunk = overlap_sentences
                    current_size = sum(len(s.split()) for s in overlap_sentences)
                else:
                    current_chunk = []
                    current_size = 0
            
            current_chunk.append(sentence)
            current_size += sentence_size
        
        # Add final chunk
        if current_chunk:
            chunk_content = ' '.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'start_sentence': len(sentences) - len(current_chunk),
                'end_sentence': len(sentences) - 1,
                'size': current_size
            })
        
        return chunks
    
    async def recursive_chunking(self, content: str, analysis: DocumentAnalysis, 
                               doc_id: str) -> List[Dict[str, Any]]:
        """
        Recursive chunking with hierarchical boundaries
        """
        config = self.strategy_configs[ChunkingStrategy.RECURSIVE_CHUNKING]
        
        def chunk_recursive(text: str, level: int = 0) -> List[Dict[str, Any]]:
            if level >= config['recursion_levels'] or len(text.split()) <= config['min_chunk_size']:
                return [{'content': text, 'level': level, 'size': len(text.split())}]
            
            # Try different splitting strategies based on level
            if level == 0 and analysis.structural_elements.get('headers'):
                # Split by headers
                return self._split_by_headers(text, level)
            elif level == 1:
                # Split by paragraphs
                return self._split_by_paragraphs(text, level)
            else:
                # Split by sentences
                return self._split_by_sentences(text, level, config)
        
        return chunk_recursive(content)
    
    async def fixed_size_chunking(self, content: str, analysis: DocumentAnalysis, 
                                doc_id: str) -> List[Dict[str, Any]]:
        """
        Fixed-size chunking with sentence boundary preservation
        """
        config = self.strategy_configs[ChunkingStrategy.FIXED_SIZE_CHUNKING]
        
        words = content.split()
        chunks = []
        
        i = 0
        while i < len(words):
            chunk_words = words[i:i + config['chunk_size']]
            chunk_content = ' '.join(chunk_words)
            
            if config['preserve_sentences']:
                # Try to end at sentence boundary
                chunk_content = self._adjust_to_sentence_boundary(chunk_content, content, i)
            
            chunks.append({
                'content': chunk_content,
                'start_word': i,
                'end_word': i + len(chunk_words),
                'size': len(chunk_words)
            })
            
            i += config['chunk_size'] - config['overlap_size']
        
        return chunks
    
    async def adaptive_chunking(self, content: str, analysis: DocumentAnalysis, 
                              doc_id: str) -> List[Dict[str, Any]]:
        """
        Adaptive chunking that combines multiple strategies
        """
        # Use different strategies for different parts of the document
        chunks = []
        
        # Start with semantic chunking
        semantic_chunks = await self.semantic_chunking(content, analysis, doc_id)
        
        # Refine chunks that are too large or too small
        for chunk in semantic_chunks:
            chunk_size = chunk['size']
            
            if chunk_size > analysis.optimal_chunk_size * 1.5:
                # Split large chunks
                sub_chunks = await self._split_large_chunk(chunk['content'])
                chunks.extend(sub_chunks)
            elif chunk_size < analysis.optimal_chunk_size * 0.5:
                # Merge small chunks if possible
                if chunks and chunks[-1]['size'] < analysis.optimal_chunk_size * 0.8:
                    chunks[-1]['content'] += ' ' + chunk['content']
                    chunks[-1]['size'] += chunk_size
                else:
                    chunks.append(chunk)
            else:
                chunks.append(chunk)
        
        return chunks
    
    async def sentence_chunking(self, content: str, analysis: DocumentAnalysis, 
                              doc_id: str) -> List[Dict[str, Any]]:
        """
        Sentence-based chunking
        """
        config = self.strategy_configs[ChunkingStrategy.SENTENCE_CHUNKING]
        
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        chunks = []
        
        i = 0
        while i < len(sentences):
            chunk_sentences = sentences[i:i + config['max_sentences']]
            chunk_content = '. '.join(chunk_sentences) + '.'
            
            chunks.append({
                'content': chunk_content,
                'sentences': chunk_sentences,
                'sentence_count': len(chunk_sentences)
            })
            
            i += config['max_sentences'] - config['overlap_sentences']
        
        return chunks
    
    async def paragraph_chunking(self, content: str, analysis: DocumentAnalysis, 
                               doc_id: str) -> List[Dict[str, Any]]:
        """
        Paragraph-based chunking
        """
        config = self.strategy_configs[ChunkingStrategy.PARAGRAPH_CHUNKING]
        
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        chunks = []
        
        i = 0
        while i < len(paragraphs):
            chunk_paragraphs = paragraphs[i:i + config['max_paragraphs']]
            chunk_content = '\n\n'.join(chunk_paragraphs)
            
            chunks.append({
                'content': chunk_content,
                'paragraphs': chunk_paragraphs,
                'paragraph_count': len(chunk_paragraphs)
            })
            
            i += config['max_paragraphs'] - config['overlap_paragraphs']
        
        return chunks
    
    async def topic_chunking(self, content: str, analysis: DocumentAnalysis, 
                           doc_id: str) -> List[Dict[str, Any]]:
        """
        Topic-based chunking using semantic similarity
        """
        config = self.strategy_configs[ChunkingStrategy.TOPIC_CHUNKING]
        
        # Split into sentences
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        
        chunks = []
        current_chunk = []
        
        for sentence in sentences:
            if not current_chunk:
                current_chunk.append(sentence)
                continue
            
            # Calculate topic similarity with current chunk
            similarity = await self._calculate_topic_similarity(
                sentence, ' '.join(current_chunk)
            )
            
            if similarity >= config['topic_threshold'] and len(current_chunk) < 10:
                # Add to current chunk
                current_chunk.append(sentence)
            else:
                # Start new chunk
                if current_chunk:
                    chunk_content = '. '.join(current_chunk) + '.'
                    chunks.append({
                        'content': chunk_content,
                        'sentences': current_chunk,
                        'topic_coherence': similarity
                    })
                current_chunk = [sentence]
        
        # Add final chunk
        if current_chunk:
            chunk_content = '. '.join(current_chunk) + '.'
            chunks.append({
                'content': chunk_content,
                'sentences': current_chunk,
                'topic_coherence': 1.0
            })
        
        return chunks
    
    async def optimize_chunks_for_retrieval(self, chunks: List[Dict[str, Any]], 
                                          analysis: DocumentAnalysis) -> List[Dict[str, Any]]:
        """
        Optimize chunks for better retrieval performance
        """
        optimized_chunks = []
        
        for chunk in chunks:
            content = chunk['content']
            
            # Add context if chunk is too short
            if len(content.split()) < 50:
                # Try to add surrounding context
                enhanced_content = await self._add_contextual_information(content, analysis)
                chunk['content'] = enhanced_content
                chunk['enhanced'] = True
            
            # Ensure chunk has enough information density
            information_density = await self._calculate_information_density(content)
            chunk['information_density'] = information_density
            
            optimized_chunks.append(chunk)
        
        return optimized_chunks
    
    async def generate_chunk_metadata(self, chunks: List[Dict[str, Any]], 
                                    analysis: DocumentAnalysis,
                                    strategy: ChunkingStrategy, 
                                    doc_id: str) -> List[Dict[str, Any]]:
        """
        Generate comprehensive metadata for chunks
        """
        final_chunks = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_id}_chunk_{i}"
            
            # Calculate chunk metrics
            semantic_coherence = await self._calculate_semantic_coherence(chunk['content'])
            topic_consistency = await self._calculate_topic_consistency(chunk['content'])
            structural_integrity = await self._calculate_structural_integrity(chunk, analysis)
            
            # Generate embedding
            embedding = await self._generate_chunk_embedding(chunk['content'])
            
            chunk_metadata = ChunkMetadata(
                chunk_id=chunk_id,
                content_type=analysis.content_type,
                chunking_strategy=strategy,
                chunk_size=chunk.get('size', len(chunk['content'].split())),
                overlap_size=chunk.get('overlap_size', 0),
                semantic_coherence=semantic_coherence,
                topic_consistency=topic_consistency,
                structural_integrity=structural_integrity,
                retrieval_optimized=True,
                parent_document_id=doc_id,
                position_in_document=i,
                sibling_chunks=[f"{doc_id}_chunk_{j}" for j in range(len(chunks)) if j != i],
                semantic_embedding=embedding
            )
            
            final_chunks.append({
                'chunk_id': chunk_id,
                'content': chunk['content'],
                'metadata': chunk_metadata.__dict__,
                'chunk_metrics': {
                    'semantic_coherence': semantic_coherence,
                    'topic_consistency': topic_consistency,
                    'structural_integrity': structural_integrity,
                    'information_density': chunk.get('information_density', 0.5)
                }
            })
        
        return final_chunks
    
    # Helper methods
    async def _split_by_headers(self, text: str, level: int) -> List[Dict[str, Any]]:
        """Split text by headers"""
        # Mock implementation
        return [{'content': text, 'level': level}]
    
    async def _split_by_paragraphs(self, text: str, level: int) -> List[Dict[str, Any]]:
        """Split text by paragraphs"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return [{'content': p, 'level': level} for p in paragraphs]
    
    async def _split_by_sentences(self, text: str, level: int, config: Dict) -> List[Dict[str, Any]]:
        """Split text by sentences"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        chunks = []
        
        for i in range(0, len(sentences), config['max_chunk_size'] // 10):
            chunk_sentences = sentences[i:i + config['max_chunk_size'] // 10]
            if chunk_sentences:
                chunks.append({
                    'content': '. '.join(chunk_sentences) + '.',
                    'level': level
                })
        
        return chunks
    
    def _adjust_to_sentence_boundary(self, chunk_content: str, original_content: str, start_pos: int) -> str:
        """Adjust chunk to end at sentence boundary"""
        # Find the last complete sentence in the chunk
        sentences = re.split(r'[.!?]+', chunk_content)
        if len(sentences) > 1:
            return '. '.join(sentences[:-1]) + '.'
        return chunk_content
    
    async def _split_large_chunk(self, content: str) -> List[Dict[str, Any]]:
        """Split large chunk into smaller ones"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', content) if s.strip()]
        mid_point = len(sentences) // 2
        
        chunk1 = '. '.join(sentences[:mid_point]) + '.' if sentences[:mid_point] else content[:len(content)//2]
        chunk2 = '. '.join(sentences[mid_point:]) + '.' if sentences[mid_point:] else content[len(content)//2:]
        
        return [
            {'content': chunk1, 'size': len(chunk1.split())},
            {'content': chunk2, 'size': len(chunk2.split())}
        ]
    
    async def _calculate_topic_similarity(self, sentence1: str, sentence2: str) -> float:
        """Calculate topic similarity between sentences"""
        # Mock implementation - in practice, use embeddings
        words1 = set(sentence1.lower().split())
        words2 = set(sentence2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    async def _add_contextual_information(self, content: str, analysis: DocumentAnalysis) -> str:
        """Add contextual information to enhance chunk"""
        # Add document type context
        context_prefix = f"[{analysis.content_type.value.replace('_', ' ').title()}] "
        return context_prefix + content
    
    async def _calculate_information_density(self, content: str) -> float:
        """Calculate information density of content"""
        words = content.split()
        unique_words = set(word.lower() for word in words if word.isalpha())
        
        return len(unique_words) / len(words) if words else 0.0
    
    async def _calculate_semantic_coherence(self, content: str) -> float:
        """Calculate semantic coherence of chunk content"""
        # Mock implementation
        return 0.8
    
    async def _calculate_topic_consistency(self, content: str) -> float:
        """Calculate topic consistency within chunk"""
        # Mock implementation
        return 0.7
    
    async def _calculate_structural_integrity(self, chunk: Dict, analysis: DocumentAnalysis) -> float:
        """Calculate structural integrity of chunk"""
        # Mock implementation
        return 0.9
    
    async def _generate_chunk_embedding(self, content: str) -> np.ndarray:
        """Generate embedding for chunk"""
        # Mock implementation
        return np.random.rand(384)
