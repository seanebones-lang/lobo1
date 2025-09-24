"""
Pydantic models for API request/response validation.
"""

from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, validator
from enum import Enum


class PromptType(str, Enum):
    """Available prompt types."""
    QA = "qa"
    SUMMARIZATION = "summarization"
    ANALYSIS = "analysis"
    CONVERSATION = "conversation"
    CODE_EXPLANATION = "code_explanation"
    CREATIVE_WRITING = "creative_writing"


class SystemRole(str, Enum):
    """Available system roles."""
    ASSISTANT = "assistant"
    EXPERT = "expert"
    ANALYST = "analyst"
    CREATIVE = "creative"
    TEACHER = "teacher"


class QueryRequest(BaseModel):
    """Request model for query endpoint."""
    question: str = Field(..., min_length=1, max_length=1000, description="The question to ask")
    prompt_type: PromptType = Field(default=PromptType.QA, description="Type of prompt to use")
    system_role: SystemRole = Field(default=SystemRole.ASSISTANT, description="System role for the AI")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    rerank_top_k: int = Field(default=3, ge=1, le=10, description="Number of documents to use after reranking")
    include_sources: bool = Field(default=True, description="Whether to include source information")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for generation")
    max_tokens: int = Field(default=1000, ge=1, le=4000, description="Maximum tokens to generate")
    model_name: Optional[str] = Field(default=None, description="Specific model to use")
    
    @validator('rerank_top_k')
    def rerank_top_k_must_be_less_than_top_k(cls, v, values):
        if 'top_k' in values and v > values['top_k']:
            raise ValueError('rerank_top_k must be less than or equal to top_k')
        return v


class QueryResponse(BaseModel):
    """Response model for query endpoint."""
    answer: str = Field(..., description="The generated answer")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source documents used")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score for the answer")
    retrieval_time: float = Field(..., ge=0.0, description="Time taken for retrieval in seconds")
    generation_time: float = Field(..., ge=0.0, description="Time taken for generation in seconds")
    total_time: float = Field(..., ge=0.0, description="Total time taken in seconds")
    model_used: Optional[str] = Field(default=None, description="Model used for generation")
    tokens_used: int = Field(default=0, ge=0, description="Number of tokens used")
    error: Optional[str] = Field(default=None, description="Error message if any")


class StreamingChunk(BaseModel):
    """Model for streaming response chunks."""
    type: str = Field(..., description="Type of chunk: content, sources, done, error")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Chunk content")
    confidence: Optional[float] = Field(default=None, description="Confidence score")
    sources: Optional[List[Dict[str, Any]]] = Field(default=None, description="Source documents")


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    file_paths: List[str] = Field(..., min_items=1, description="Paths to documents to upload")
    chunk_method: str = Field(default="recursive", description="Chunking method to use")
    chunk_size: int = Field(default=1000, ge=100, le=2000, description="Size of chunks")
    chunk_overlap: int = Field(default=200, ge=0, le=500, description="Overlap between chunks")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata to add to documents")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool = Field(..., description="Whether upload was successful")
    documents_processed: int = Field(..., ge=0, description="Number of documents processed")
    chunks_created: int = Field(..., ge=0, description="Number of chunks created")
    processing_time: float = Field(..., ge=0.0, description="Time taken for processing")
    error: Optional[str] = Field(default=None, description="Error message if any")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: str = Field(..., description="Current timestamp")
    components: Dict[str, Any] = Field(..., description="Component status")


class StatsResponse(BaseModel):
    """Response model for system statistics."""
    llm_stats: Dict[str, Any] = Field(..., description="LLM statistics")
    embedding_stats: Dict[str, Any] = Field(..., description="Embedding statistics")
    retriever_stats: Dict[str, Any] = Field(..., description="Retriever statistics")
    vector_store_info: Dict[str, Any] = Field(..., description="Vector store information")
    uptime: float = Field(..., description="System uptime in seconds")


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")


class ConversationRequest(BaseModel):
    """Request model for conversational queries."""
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    conversation_history: List[Dict[str, str]] = Field(default=[], description="Previous conversation")
    system_role: SystemRole = Field(default=SystemRole.ASSISTANT, description="System role")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    temperature: float = Field(default=0.1, ge=0.0, le=2.0, description="Temperature for generation")


class ConversationResponse(BaseModel):
    """Response model for conversational queries."""
    response: str = Field(..., description="AI response")
    conversation_id: str = Field(..., description="Unique conversation identifier")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source documents")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    processing_time: float = Field(..., ge=0.0, description="Processing time in seconds")


class BatchQueryRequest(BaseModel):
    """Request model for batch queries."""
    queries: List[str] = Field(..., min_items=1, max_items=10, description="List of queries to process")
    prompt_type: PromptType = Field(default=PromptType.QA, description="Type of prompt to use")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of documents to retrieve")
    include_sources: bool = Field(default=True, description="Whether to include sources")


class BatchQueryResponse(BaseModel):
    """Response model for batch queries."""
    results: List[QueryResponse] = Field(..., description="Results for each query")
    total_processing_time: float = Field(..., ge=0.0, description="Total processing time")
    success_count: int = Field(..., ge=0, description="Number of successful queries")
    error_count: int = Field(..., ge=0, description="Number of failed queries")

