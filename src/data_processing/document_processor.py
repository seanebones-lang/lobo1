"""
Document processing module for loading and preprocessing various document types.
"""

import os
import re
import html
from pathlib import Path
from typing import List, Dict, Any, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    UnstructuredURLLoader,
    WebBaseLoader
)
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_openai import OpenAIEmbeddings


class TextCleaner:
    """Utility class for cleaning and preprocessing text."""
    
    def __init__(self):
        self.cleaning_patterns = [
            (r'\s+', ' '),  # Remove extra whitespace
            (r'<[^>]+>', ''),  # Remove HTML tags
            (r'[^\w\s.,!?;:]', ''),  # Remove special characters but keep meaningful punctuation
        ]
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text."""
        if not text:
            return ""
        
        # Remove HTML entities
        text = html.unescape(text)
        
        # Apply cleaning patterns
        for pattern, replacement in self.cleaning_patterns:
            text = re.sub(pattern, replacement, text)
        
        return text.strip()
    
    def clean_documents(self, documents: List[Document]) -> List[Document]:
        """Clean a list of documents."""
        cleaned_docs = []
        for doc in documents:
            cleaned_content = self.clean_text(doc.page_content)
            if cleaned_content:  # Only keep non-empty documents
                doc.page_content = cleaned_content
                cleaned_docs.append(doc)
        return cleaned_docs


class DocumentProcessor:
    """Main class for processing various document types."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        self.loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.txt': TextLoader,
        }
        self.text_cleaner = TextCleaner()
        self.openai_api_key = openai_api_key
        
        # Initialize text splitters
        self.recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        
        # Semantic splitter (requires OpenAI API key)
        if openai_api_key:
            embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.semantic_splitter = SemanticChunker(
                embeddings,
                breakpoint_threshold_type="percentile"
            )
        else:
            self.semantic_splitter = None
    
    def load_documents(self, file_paths: List[str]) -> List[Document]:
        """Load documents from file paths."""
        documents = []
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                print(f"Warning: File {file_path} does not exist")
                continue
            
            try:
                if path.suffix in self.loaders:
                    loader = self.loaders[path.suffix](str(path))
                    docs = loader.load()
                    documents.extend(docs)
                else:
                    print(f"Warning: Unsupported file type {path.suffix}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        return documents
    
    def load_web_documents(self, urls: List[str]) -> List[Document]:
        """Load documents from URLs."""
        documents = []
        
        for url in urls:
            try:
                loader = WebBaseLoader(url)
                docs = loader.load()
                documents.extend(docs)
            except Exception as e:
                print(f"Error loading URL {url}: {e}")
        
        return documents
    
    def chunk_documents(
        self, 
        documents: List[Document], 
        method: str = "recursive",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """Chunk documents using specified method."""
        if not documents:
            return []
        
        # Clean documents first
        cleaned_docs = self.text_cleaner.clean_documents(documents)
        
        if method == "semantic" and self.semantic_splitter:
            return self.semantic_splitter.split_documents(cleaned_docs)
        else:
            # Update chunk size if different from default
            if chunk_size != 1000 or chunk_overlap != 200:
                splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    length_function=len,
                )
                return splitter.split_documents(cleaned_docs)
            else:
                return self.recursive_splitter.split_documents(cleaned_docs)
    
    def process_documents(
        self,
        file_paths: Optional[List[str]] = None,
        urls: Optional[List[str]] = None,
        chunk_method: str = "recursive",
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ) -> List[Document]:
        """Complete document processing pipeline."""
        documents = []
        
        # Load from files
        if file_paths:
            file_docs = self.load_documents(file_paths)
            documents.extend(file_docs)
        
        # Load from URLs
        if urls:
            web_docs = self.load_web_documents(urls)
            documents.extend(web_docs)
        
        if not documents:
            return []
        
        # Chunk documents
        chunked_docs = self.chunk_documents(
            documents, 
            method=chunk_method,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        
        return chunked_docs
    
    def add_metadata(self, documents: List[Document], metadata: Dict[str, Any]) -> List[Document]:
        """Add metadata to documents."""
        for doc in documents:
            doc.metadata.update(metadata)
        return documents

