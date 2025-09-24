"""
Prompt management module for different types of queries and tasks.
"""

from typing import Dict, Any, Optional, List
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
import json


class PromptManager:
    """Manages different types of prompts for various RAG tasks."""
    
    def __init__(self):
        """Initialize prompt manager with predefined templates."""
        self.prompts = self._initialize_prompts()
    
    def _initialize_prompts(self) -> Dict[str, ChatPromptTemplate]:
        """Initialize all prompt templates."""
        return {
            "qa": self._get_qa_prompt(),
            "summarization": self._get_summarization_prompt(),
            "analysis": self._get_analysis_prompt(),
            "conversation": self._get_conversation_prompt(),
            "code_explanation": self._get_code_explanation_prompt(),
            "creative_writing": self._get_creative_writing_prompt()
        }
    
    def _get_qa_prompt(self) -> ChatPromptTemplate:
        """Get question-answering prompt template."""
        return ChatPromptTemplate.from_template("""
You are an expert AI assistant with access to relevant context. Use the following context to answer the question accurately and comprehensively.

Context:
{context}

Question: {question}

Guidelines:
- Provide a clear, accurate, and well-structured answer
- If the context doesn't contain enough information to answer the question, say so explicitly
- Cite relevant sources or sections when possible
- Use markdown formatting for better readability (headers, lists, code blocks, etc.)
- If you're uncertain about any part of your answer, express that uncertainty
- Keep your answer focused and concise while being thorough

Answer:
""")
    
    def _get_summarization_prompt(self) -> ChatPromptTemplate:
        """Get text summarization prompt template."""
        return ChatPromptTemplate.from_template("""
Summarize the following text in a clear and concise manner. Focus on the key points and main ideas.

Text: {text}

Summary Guidelines:
- Capture the main points and key information
- Maintain the original tone and intent
- Use bullet points or numbered lists for better readability
- Keep the summary proportional to the original text length
- Highlight any important conclusions or recommendations

Summary:
""")
    
    def _get_analysis_prompt(self) -> ChatPromptTemplate:
        """Get analytical prompt template."""
        return ChatPromptTemplate.from_template("""
Analyze the following information and provide insights, patterns, and recommendations.

Context:
{context}

Analysis Request: {question}

Analysis Guidelines:
- Identify key patterns, trends, or relationships
- Provide evidence-based insights
- Consider multiple perspectives
- Highlight potential implications or consequences
- Suggest actionable recommendations when appropriate
- Use data and examples to support your analysis

Analysis:
""")
    
    def _get_conversation_prompt(self) -> ChatPromptTemplate:
        """Get conversational prompt template."""
        return ChatPromptTemplate.from_template("""
You are a helpful AI assistant engaged in a conversation. Use the provided context to maintain continuity and provide relevant responses.

Context:
{context}

Conversation History:
{conversation_history}

Current Message: {message}

Guidelines:
- Maintain conversational flow and context
- Be engaging and helpful
- Reference previous parts of the conversation when relevant
- Ask clarifying questions if needed
- Keep responses natural and conversational

Response:
""")
    
    def _get_code_explanation_prompt(self) -> ChatPromptTemplate:
        """Get code explanation prompt template."""
        return ChatPromptTemplate.from_template("""
Explain the following code in detail, including its purpose, functionality, and key concepts.

Code:
{code}

Context (if available):
{context}

Explanation Guidelines:
- Explain what the code does and why it's useful
- Break down complex logic into understandable parts
- Highlight important functions, classes, or algorithms
- Mention any potential issues or improvements
- Use code examples to illustrate concepts when helpful
- Format code explanations clearly with markdown

Explanation:
""")
    
    def _get_creative_writing_prompt(self) -> ChatPromptTemplate:
        """Get creative writing prompt template."""
        return ChatPromptTemplate.from_template("""
You are a creative writing assistant. Use the provided context and inspiration to create engaging content.

Context/Inspiration:
{context}

Writing Task: {task}

Creative Guidelines:
- Be imaginative and engaging
- Maintain consistency with the provided context
- Use vivid descriptions and compelling language
- Structure your writing clearly
- Adapt your style to the requested format (story, poem, article, etc.)
- Be original while drawing from the context

Creative Content:
""")
    
    def get_prompt(self, prompt_type: str) -> ChatPromptTemplate:
        """Get a specific prompt template."""
        if prompt_type not in self.prompts:
            raise ValueError(f"Unknown prompt type: {prompt_type}. Available types: {list(self.prompts.keys())}")
        return self.prompts[prompt_type]
    
    def format_prompt(
        self, 
        prompt_type: str, 
        **kwargs
    ) -> str:
        """Format a prompt with the given parameters."""
        prompt_template = self.get_prompt(prompt_type)
        return prompt_template.format(**kwargs)
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt types."""
        return list(self.prompts.keys())
    
    def create_custom_prompt(
        self, 
        template: str, 
        prompt_name: str
    ) -> ChatPromptTemplate:
        """Create a custom prompt template."""
        custom_prompt = ChatPromptTemplate.from_template(template)
        self.prompts[prompt_name] = custom_prompt
        return custom_prompt
    
    def get_system_message(self, role: str = "assistant") -> SystemMessage:
        """Get a system message for the specified role."""
        system_prompts = {
            "assistant": "You are a helpful AI assistant that provides accurate and useful information.",
            "expert": "You are an expert in your field with deep knowledge and experience.",
            "analyst": "You are a data analyst who provides insights and recommendations based on evidence.",
            "creative": "You are a creative writer who produces engaging and original content.",
            "teacher": "You are a patient and knowledgeable teacher who explains concepts clearly."
        }
        
        content = system_prompts.get(role, system_prompts["assistant"])
        return SystemMessage(content=content)
    
    def format_with_system_message(
        self, 
        prompt_type: str, 
        system_role: str = "assistant",
        **kwargs
    ) -> List[BaseMessage]:
        """Format a prompt with a system message."""
        system_message = self.get_system_message(system_role)
        prompt_template = self.get_prompt(prompt_type)
        
        # Format the human message
        human_content = prompt_template.format(**kwargs)
        human_message = HumanMessage(content=human_content)
        
        return [system_message, human_message]
    
    def get_prompt_metadata(self, prompt_type: str) -> Dict[str, Any]:
        """Get metadata about a prompt type."""
        metadata = {
            "qa": {
                "description": "Question-answering with context",
                "use_cases": ["factual queries", "information retrieval", "research questions"],
                "required_params": ["context", "question"]
            },
            "summarization": {
                "description": "Text summarization and condensation",
                "use_cases": ["document summaries", "meeting notes", "article abstracts"],
                "required_params": ["text"]
            },
            "analysis": {
                "description": "Analytical thinking and insights",
                "use_cases": ["data analysis", "trend identification", "strategic planning"],
                "required_params": ["context", "question"]
            },
            "conversation": {
                "description": "Conversational AI with memory",
                "use_cases": ["chatbots", "customer service", "personal assistants"],
                "required_params": ["context", "conversation_history", "message"]
            },
            "code_explanation": {
                "description": "Code analysis and explanation",
                "use_cases": ["code reviews", "documentation", "learning"],
                "required_params": ["code"]
            },
            "creative_writing": {
                "description": "Creative content generation",
                "use_cases": ["story writing", "content creation", "marketing copy"],
                "required_params": ["context", "task"]
            }
        }
        
        return metadata.get(prompt_type, {"description": "Unknown prompt type"})

