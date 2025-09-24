"""
Mega Document Processor
Processes every document type with advanced features.
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import pandas as pd
from docx import Document
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
import cv2
import numpy as np

class MegaDocumentProcessor:
    """Processes every document type with advanced features"""
    
    def __init__(self, config):
        self.config = config
        self.loaders = self.initialize_loaders()
        self.preprocessors = self.initialize_preprocessors()
        self.extractors = self.initialize_extractors()
        self.entity_extractors = self.initialize_entity_extractors()
    
    def initialize_loaders(self) -> Dict[str, Any]:
        """Initialize all document loaders"""
        return {
            'pdf': AdvancedPDFLoader(),
            'docx': SmartDOCXLoader(),
            'html': WebPageLoader(),
            'txt': TextLoader(),
            'csv': DataFrameLoader(),
            'xlsx': ExcelLoader(),
            'pptx': PowerPointLoader(),
            'images': MultiModalImageLoader(),
            'audio': SpeechToTextLoader(),
            'video': VideoProcessor(),
            'code': CodebaseLoader(),
            'emails': EmailParser(),
            'database': DatabaseExtractor()
        }
    
    def initialize_preprocessors(self) -> Dict[str, Any]:
        """Initialize content preprocessors"""
        return {
            'pdf': PDFPreprocessor(),
            'html': HTMLPreprocessor(),
            'text': TextPreprocessor(),
            'image': ImagePreprocessor(),
            'audio': AudioPreprocessor(),
            'video': VideoPreprocessor(),
            'default': DefaultPreprocessor()
        }
    
    def initialize_extractors(self) -> Dict[str, Any]:
        """Initialize content extractors"""
        return {
            'tables': TableExtractor(),
            'images': ImageExtractor(),
            'code': CodeExtractor(),
            'metadata': MetadataExtractor(),
            'structure': StructureExtractor()
        }
    
    def initialize_entity_extractors(self) -> List[Any]:
        """Initialize entity extractors"""
        return [
            SpacyEntityExtractor(),
            TransformersNER(),
            RuleBasedExtractor(),
            DictionaryBasedExtractor()
        ]
    
    async def process_document(self, file_path: str, metadata: Dict = None) -> Dict:
        """Process any document type with full feature extraction"""
        
        file_ext = file_path.split('.')[-1].lower()
        loader = self.loaders.get(file_ext, self.loaders['txt'])
        
        try:
            print(f"📄 Processing {file_ext.upper()} document: {file_path}")
            
            # Load document
            raw_content = await loader.load(file_path)
            
            # Extract metadata
            enhanced_metadata = await self.extract_enhanced_metadata(raw_content, metadata, file_ext)
            
            # Preprocess content
            processed_content = await self.preprocess_content(raw_content, file_ext)
            
            # Extract entities and relationships
            entities = await self.extract_entities(processed_content)
            relationships = await self.extract_relationships(entities, processed_content)
            
            # Extract additional content (tables, images, code)
            extracted_content = await self.extract_additional_content(raw_content, file_ext)
            
            # Generate embeddings for chunks
            chunks = await self.chunk_document(processed_content, file_ext)
            chunk_embeddings = await self.generate_chunk_embeddings(chunks)
            
            # Build document graph
            document_graph = await self.build_document_graph(chunks, entities, relationships)
            
            result = {
                'content': processed_content,
                'chunks': chunks,
                'embeddings': chunk_embeddings,
                'metadata': enhanced_metadata,
                'entities': entities,
                'relationships': relationships,
                'document_graph': document_graph,
                'extracted_content': extracted_content,
                'processing_timestamp': datetime.now(),
                'content_hash': self.calculate_content_hash(processed_content),
                'file_type': file_ext,
                'processing_stats': {
                    'chunk_count': len(chunks),
                    'entity_count': len(entities),
                    'relationship_count': len(relationships),
                    'processing_time': 0  # Will be calculated
                }
            }
            
            print(f"✅ Successfully processed {file_ext.upper()} document")
            return result
            
        except Exception as e:
            await self.handle_processing_error(file_path, e)
            raise
    
    async def extract_enhanced_metadata(self, content: Any, metadata: Dict, file_type: str) -> Dict:
        """Extract comprehensive metadata from document"""
        
        base_metadata = {
            'file_type': file_type,
            'processing_timestamp': datetime.now().isoformat(),
            'content_length': len(str(content)) if content else 0,
            'language': await self.detect_language(content),
            'encoding': 'utf-8'
        }
        
        # Add file-specific metadata
        if file_type == 'pdf':
            base_metadata.update(await self.extract_pdf_metadata(content))
        elif file_type == 'html':
            base_metadata.update(await self.extract_html_metadata(content))
        elif file_type == 'image':
            base_metadata.update(await self.extract_image_metadata(content))
        
        # Merge with provided metadata
        if metadata:
            base_metadata.update(metadata)
        
        return base_metadata
    
    async def preprocess_content(self, content: Any, file_type: str) -> Any:
        """Advanced content preprocessing pipeline"""
        preprocessor = self.preprocessors.get(file_type, self.preprocessors['default'])
        
        # Apply preprocessing pipeline
        pipeline = [
            'clean_html',
            'remove_noise',
            'normalize_text',
            'detect_language',
            'handle_encoding',
            'extract_tables',
            'extract_images',
            'extract_code_blocks'
        ]
        
        processed_content = content
        for step in pipeline:
            processed_content = await preprocessor.apply_step(step, processed_content)
        
        return processed_content
    
    async def extract_entities(self, content: str) -> List[Dict]:
        """Extract entities using ensemble approach"""
        all_entities = []
        
        for extractor in self.entity_extractors:
            try:
                entities = await extractor.extract(content)
                all_entities.extend(entities)
            except Exception as e:
                print(f"Entity extraction failed with {extractor.__class__.__name__}: {e}")
        
        # Merge and deduplicate entities
        return self.merge_entities(all_entities)
    
    async def extract_relationships(self, entities: List[Dict], content: str) -> List[Dict]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction based on proximity
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i+1:], i+1):
                # Check if entities appear near each other in content
                if self.entities_are_related(entity1, entity2, content):
                    relationships.append({
                        'source': entity1['text'],
                        'target': entity2['text'],
                        'type': 'related',
                        'confidence': 0.8,
                        'context': self.extract_relationship_context(entity1, entity2, content)
                    })
        
        return relationships
    
    async def extract_additional_content(self, content: Any, file_type: str) -> Dict:
        """Extract additional content like tables, images, code"""
        extracted = {
            'tables': [],
            'images': [],
            'code_blocks': [],
            'links': [],
            'formulas': []
        }
        
        # Extract based on file type
        if file_type == 'pdf':
            extracted['tables'] = await self.extractors['tables'].extract_from_pdf(content)
            extracted['images'] = await self.extractors['images'].extract_from_pdf(content)
        elif file_type == 'html':
            extracted['links'] = await self.extract_links(content)
            extracted['images'] = await self.extractors['images'].extract_from_html(content)
        elif file_type in ['py', 'js', 'java', 'cpp']:
            extracted['code_blocks'] = await self.extractors['code'].extract(content)
        
        return extracted
    
    async def chunk_document(self, content: str, file_type: str) -> List[Dict]:
        """Intelligent document chunking"""
        chunking_strategy = self.select_chunking_strategy(file_type, content)
        
        if chunking_strategy == 'semantic':
            chunks = await self.semantic_chunking(content)
        elif chunking_strategy == 'recursive':
            chunks = await self.recursive_chunking(content)
        else:
            chunks = await self.fixed_size_chunking(content)
        
        # Add metadata to chunks
        for i, chunk in enumerate(chunks):
            chunk['chunk_id'] = f"{file_type}_{i}"
            chunk['chunk_index'] = i
            chunk['chunk_type'] = self.classify_chunk_type(chunk['content'])
        
        return chunks
    
    def select_chunking_strategy(self, file_type: str, content: str) -> str:
        """Select optimal chunking strategy"""
        if file_type == 'pdf':
            return 'semantic'  # Better for PDFs with structure
        elif file_type == 'code':
            return 'recursive'  # Better for code files
        elif len(content) < 1000:
            return 'fixed_size'  # Simple for short content
        else:
            return 'semantic'  # Default to semantic
    
    async def semantic_chunking(self, content: str) -> List[Dict]:
        """Semantic chunking based on content meaning"""
        # Mock implementation - in practice, use sentence transformers
        sentences = content.split('. ')
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk + sentence) < 500:  # Max chunk size
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append({'content': current_chunk.strip()})
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append({'content': current_chunk.strip()})
        
        return chunks
    
    async def recursive_chunking(self, content: str) -> List[Dict]:
        """Recursive chunking for structured content"""
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        chunks = []
        
        for para in paragraphs:
            if len(para) > 1000:  # Split long paragraphs
                sentences = para.split('. ')
                current_chunk = ""
                
                for sentence in sentences:
                    if len(current_chunk + sentence) < 500:
                        current_chunk += sentence + ". "
                    else:
                        if current_chunk:
                            chunks.append({'content': current_chunk.strip()})
                        current_chunk = sentence + ". "
                
                if current_chunk:
                    chunks.append({'content': current_chunk.strip()})
            else:
                chunks.append({'content': para.strip()})
        
        return chunks
    
    async def fixed_size_chunking(self, content: str) -> List[Dict]:
        """Fixed size chunking"""
        chunk_size = 500
        overlap = 50
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            chunk_content = content[start:end]
            
            chunks.append({'content': chunk_content})
            start = end - overlap
        
        return chunks
    
    async def generate_chunk_embeddings(self, chunks: List[Dict]) -> List[List[float]]:
        """Generate embeddings for document chunks"""
        # Mock implementation - in practice, use sentence transformers
        embeddings = []
        
        for chunk in chunks:
            # Simple hash-based embedding for demonstration
            content_hash = hashlib.md5(chunk['content'].encode()).hexdigest()
            embedding = [float(int(content_hash[i:i+2], 16)) / 255.0 for i in range(0, len(content_hash), 2)][:384]
            embeddings.append(embedding)
        
        return embeddings
    
    async def build_document_graph(self, chunks: List[Dict], entities: List[Dict], relationships: List[Dict]) -> Dict:
        """Build document knowledge graph"""
        graph = {
            'nodes': [],
            'edges': [],
            'chunk_entities': {},
            'entity_relationships': relationships
        }
        
        # Add chunk nodes
        for i, chunk in enumerate(chunks):
            graph['nodes'].append({
                'id': f"chunk_{i}",
                'type': 'chunk',
                'content': chunk['content'][:100] + "...",
                'chunk_id': chunk.get('chunk_id', f"chunk_{i}")
            })
        
        # Add entity nodes
        for entity in entities:
            graph['nodes'].append({
                'id': entity['text'],
                'type': 'entity',
                'entity_type': entity.get('type', 'unknown'),
                'confidence': entity.get('confidence', 0.5)
            })
        
        # Add edges between chunks and entities
        for i, chunk in enumerate(chunks):
            chunk_entities = []
            for entity in entities:
                if entity['text'].lower() in chunk['content'].lower():
                    chunk_entities.append(entity['text'])
                    graph['edges'].append({
                        'source': f"chunk_{i}",
                        'target': entity['text'],
                        'type': 'contains'
                    })
            graph['chunk_entities'][f"chunk_{i}"] = chunk_entities
        
        return graph
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate content hash for deduplication"""
        return hashlib.sha256(content.encode()).hexdigest()
    
    def classify_chunk_type(self, content: str) -> str:
        """Classify chunk type based on content"""
        if any(keyword in content.lower() for keyword in ['function', 'def', 'class', 'import']):
            return 'code'
        elif any(keyword in content.lower() for keyword in ['table', 'row', 'column']):
            return 'table'
        elif any(keyword in content.lower() for keyword in ['image', 'figure', 'diagram']):
            return 'image'
        else:
            return 'text'
    
    def entities_are_related(self, entity1: Dict, entity2: Dict, content: str) -> bool:
        """Check if two entities are related based on proximity in content"""
        # Simple proximity check
        pos1 = content.lower().find(entity1['text'].lower())
        pos2 = content.lower().find(entity2['text'].lower())
        
        if pos1 == -1 or pos2 == -1:
            return False
        
        distance = abs(pos1 - pos2)
        return distance < 200  # Within 200 characters
    
    def extract_relationship_context(self, entity1: Dict, entity2: Dict, content: str) -> str:
        """Extract context around relationship between entities"""
        pos1 = content.lower().find(entity1['text'].lower())
        pos2 = content.lower().find(entity2['text'].lower())
        
        start = min(pos1, pos2) - 50
        end = max(pos1, pos2) + 50
        
        return content[max(0, start):min(len(content), end)]
    
    async def detect_language(self, content: str) -> str:
        """Detect document language"""
        # Simple language detection - in practice, use langdetect
        if any(char in content for char in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'):
            return 'ru'
        elif any(char in content for char in 'àáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿ'):
            return 'fr'
        else:
            return 'en'
    
    async def extract_pdf_metadata(self, pdf_doc) -> Dict:
        """Extract PDF-specific metadata"""
        return {
            'page_count': len(pdf_doc) if hasattr(pdf_doc, '__len__') else 1,
            'title': getattr(pdf_doc, 'metadata', {}).get('title', ''),
            'author': getattr(pdf_doc, 'metadata', {}).get('author', ''),
            'creation_date': getattr(pdf_doc, 'metadata', {}).get('creationDate', '')
        }
    
    async def extract_html_metadata(self, html_content: str) -> Dict:
        """Extract HTML-specific metadata"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        return {
            'title': soup.title.string if soup.title else '',
            'meta_description': soup.find('meta', attrs={'name': 'description'}),
            'links_count': len(soup.find_all('a')),
            'images_count': len(soup.find_all('img'))
        }
    
    async def extract_image_metadata(self, image) -> Dict:
        """Extract image-specific metadata"""
        if hasattr(image, 'size'):
            return {
                'width': image.size[0],
                'height': image.size[1],
                'format': getattr(image, 'format', 'unknown')
            }
        return {}
    
    async def extract_links(self, html_content: str) -> List[str]:
        """Extract links from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return [link for link in links if link]
    
    def merge_entities(self, entities: List[Dict]) -> List[Dict]:
        """Merge and deduplicate entities"""
        seen = set()
        merged = []
        
        for entity in entities:
            key = (entity['text'].lower(), entity.get('type', ''))
            if key not in seen:
                seen.add(key)
                merged.append(entity)
        
        return merged
    
    async def handle_processing_error(self, file_path: str, error: Exception):
        """Handle document processing errors"""
        print(f"❌ Error processing {file_path}: {error}")
        # In production, log to error tracking system

# Mock loader classes
class AdvancedPDFLoader:
    async def load(self, file_path: str):
        return "Mock PDF content"
    
class SmartDOCXLoader:
    async def load(self, file_path: str):
        return "Mock DOCX content"
    
class WebPageLoader:
    async def load(self, file_path: str):
        return "Mock HTML content"
    
class TextLoader:
    async def load(self, file_path: str):
        return "Mock text content"
    
class DataFrameLoader:
    async def load(self, file_path: str):
        return "Mock CSV content"
    
class ExcelLoader:
    async def load(self, file_path: str):
        return "Mock Excel content"
    
class PowerPointLoader:
    async def load(self, file_path: str):
        return "Mock PowerPoint content"
    
class MultiModalImageLoader:
    async def load(self, file_path: str):
        return "Mock image content"
    
class SpeechToTextLoader:
    async def load(self, file_path: str):
        return "Mock audio transcription"
    
class VideoProcessor:
    async def load(self, file_path: str):
        return "Mock video content"
    
class CodebaseLoader:
    async def load(self, file_path: str):
        return "Mock code content"
    
class EmailParser:
    async def load(self, file_path: str):
        return "Mock email content"
    
class DatabaseExtractor:
    async def load(self, file_path: str):
        return "Mock database content"

# Mock preprocessor classes
class PDFPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class HTMLPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class TextPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class ImagePreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class AudioPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class VideoPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

class DefaultPreprocessor:
    async def apply_step(self, step: str, content: Any):
        return content

# Mock extractor classes
class TableExtractor:
    async def extract_from_pdf(self, content):
        return []

class ImageExtractor:
    async def extract_from_pdf(self, content):
        return []
    
    async def extract_from_html(self, content):
        return []

class CodeExtractor:
    async def extract(self, content):
        return []

class MetadataExtractor:
    async def extract(self, content):
        return {}

class StructureExtractor:
    async def extract(self, content):
        return {}

# Mock entity extractor classes
class SpacyEntityExtractor:
    async def extract(self, content: str):
        return [{'text': 'Mock Entity', 'type': 'PERSON', 'confidence': 0.9}]

class TransformersNER:
    async def extract(self, content: str):
        return [{'text': 'Mock Entity', 'type': 'ORG', 'confidence': 0.8}]

class RuleBasedExtractor:
    async def extract(self, content: str):
        return [{'text': 'Mock Entity', 'type': 'LOCATION', 'confidence': 0.7}]

class DictionaryBasedExtractor:
    async def extract(self, content: str):
        return [{'text': 'Mock Entity', 'type': 'MISC', 'confidence': 0.6}]
