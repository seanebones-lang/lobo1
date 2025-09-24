"""
Sales RAG Integration Module
Integrates comprehensive sales knowledge into the RAG system for enhanced sales-focused responses
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class SalesRAGIntegration:
    """Integrates sales knowledge into RAG system for enhanced sales-focused responses"""
    
    def __init__(self, knowledge_base_path: str = "./sales_knowledge_documents"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.sales_knowledge = self._load_sales_knowledge()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    def _load_sales_knowledge(self) -> Dict[str, Any]:
        """Load comprehensive sales knowledge from files"""
        knowledge = {
            "sales_fundamentals": {},
            "customer_psychology": {},
            "conversation_patterns": {},
            "objection_handling": {},
            "closing_techniques": {}
        }
        
        # Load from markdown files if they exist
        if self.knowledge_base_path.exists():
            for file_path in self.knowledge_base_path.glob("*.md"):
                content = file_path.read_text(encoding='utf-8')
                knowledge[file_path.stem] = content
        
        return knowledge
    
    def create_sales_documents(self) -> List[Document]:
        """Create document chunks from sales knowledge for RAG system"""
        documents = []
        
        # Create documents from sales knowledge
        for category, content in self.sales_knowledge.items():
            if isinstance(content, str) and content.strip():
                # Split content into chunks
                chunks = self.text_splitter.split_text(content)
                
                for i, chunk in enumerate(chunks):
                    doc = Document(
                        page_content=chunk,
                        metadata={
                            "category": category,
                            "chunk_id": i,
                            "source": f"{category}.md",
                            "type": "sales_knowledge",
                            "personality": "sales_focused_friendly_caring"
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    def enhance_query_for_sales(self, query: str) -> Dict[str, Any]:
        """Enhance query with sales context and intent classification"""
        
        # Classify query intent
        intent = self._classify_sales_intent(query)
        
        # Extract key information
        extracted_info = self._extract_query_info(query)
        
        # Generate sales context
        sales_context = self._generate_sales_context(intent, extracted_info)
        
        return {
            "original_query": query,
            "intent": intent,
            "extracted_info": extracted_info,
            "sales_context": sales_context,
            "enhanced_query": f"{query} [Sales Context: {sales_context}]"
        }
    
    def _classify_sales_intent(self, query: str) -> str:
        """Classify the sales intent of the query"""
        query_lower = query.lower()
        
        # Intent classification patterns
        intent_patterns = {
            "pricing": ["price", "cost", "expensive", "budget", "how much", "afford"],
            "scheduling": ["when", "time", "schedule", "appointment", "available", "book"],
            "concerns": ["pain", "hurt", "uncomfortable", "worried", "scared", "concerned"],
            "design": ["design", "style", "idea", "concept", "look like", "show me"],
            "process": ["how", "process", "what happens", "steps", "procedure"],
            "aftercare": ["heal", "care", "after", "recovery", "maintenance"],
            "booking": ["book", "schedule", "appointment", "reserve", "sign up"],
            "general_info": ["tell me", "explain", "what is", "information"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return "general_info"
    
    def _extract_query_info(self, query: str) -> Dict[str, Any]:
        """Extract relevant information from the query"""
        query_lower = query.lower()
        
        extracted = {
            "tattoo_type": None,
            "body_part": None,
            "size": None,
            "urgency": None,
            "budget_mentioned": False,
            "experience_level": None
        }
        
        # Extract tattoo type
        tattoo_types = ["realistic", "traditional", "geometric", "watercolor", "blackwork", "dotwork"]
        for tattoo_type in tattoo_types:
            if tattoo_type in query_lower:
                extracted["tattoo_type"] = tattoo_type
                break
        
        # Extract body part
        body_parts = ["arm", "back", "chest", "leg", "hand", "neck", "shoulder", "ribs"]
        for body_part in body_parts:
            if body_part in query_lower:
                extracted["body_part"] = body_part
                break
        
        # Extract size indicators
        size_indicators = ["small", "medium", "large", "sleeve", "back piece", "tiny", "huge"]
        for size in size_indicators:
            if size in query_lower:
                extracted["size"] = size
                break
        
        # Check for urgency
        urgency_words = ["urgent", "asap", "soon", "quickly", "fast"]
        extracted["urgency"] = any(word in query_lower for word in urgency_words)
        
        # Check for budget mention
        budget_words = ["budget", "afford", "expensive", "cost", "price"]
        extracted["budget_mentioned"] = any(word in query_lower for word in budget_words)
        
        # Check experience level
        if any(word in query_lower for word in ["first", "never had", "new", "beginner"]):
            extracted["experience_level"] = "first_time"
        elif any(word in query_lower for word in ["before", "previous", "other tattoos"]):
            extracted["experience_level"] = "experienced"
        
        return extracted
    
    def _generate_sales_context(self, intent: str, extracted_info: Dict[str, Any]) -> str:
        """Generate sales context based on intent and extracted information"""
        context_parts = []
        
        # Add intent-based context
        if intent == "pricing":
            context_parts.append("Client is asking about pricing - focus on value proposition and payment options")
        elif intent == "scheduling":
            context_parts.append("Client wants to schedule - emphasize availability and urgency")
        elif intent == "concerns":
            context_parts.append("Client has concerns - address with empathy and reassurance")
        elif intent == "design":
            context_parts.append("Client discussing design - build excitement and show expertise")
        elif intent == "booking":
            context_parts.append("Client ready to book - use assumptive closing techniques")
        
        # Add extracted info context
        if extracted_info["tattoo_type"]:
            context_parts.append(f"Tattoo type: {extracted_info['tattoo_type']}")
        
        if extracted_info["body_part"]:
            context_parts.append(f"Body placement: {extracted_info['body_part']}")
        
        if extracted_info["size"]:
            context_parts.append(f"Size: {extracted_info['size']}")
        
        if extracted_info["urgency"]:
            context_parts.append("High urgency - create appropriate urgency")
        
        if extracted_info["budget_mentioned"]:
            context_parts.append("Budget-sensitive - focus on value and options")
        
        if extracted_info["experience_level"] == "first_time":
            context_parts.append("First-time client - provide extra reassurance and education")
        elif extracted_info["experience_level"] == "experienced":
            context_parts.append("Experienced client - can move faster through process")
        
        return " | ".join(context_parts)
    
    def get_sales_personality_prompt(self) -> str:
        """Get comprehensive sales personality prompt"""
        return """
You are a friendly, caring, and sales-focused tattoo consultant with the following personality traits:

PERSONALITY:
- Tone: friendly, caring, and sales-focused
- Communication style: consultative and empathetic  
- Sales approach: relationship-building and value-driven
- Emotional intelligence: high - reads client needs and emotions
- Closing style: gentle and assumptive

SALES PRINCIPLES:
1. Always prioritize the client's needs and concerns
2. Build genuine rapport and trust through active listening
3. Focus on value and benefits, not just features
4. Handle objections with empathy and understanding
5. Guide conversations toward positive outcomes
6. Maintain a caring, supportive attitude throughout

CONVERSATION STYLE:
- Use warm, welcoming language that shows genuine interest
- Ask open-ended questions to understand their tattoo vision
- Address concerns directly and empathetically
- Create excitement about their tattoo journey
- Always be helpful and solution-oriented
- Show enthusiasm for their personal expression
- Be patient and understanding with concerns

SALES TECHNIQUES:
- Consultative selling: Ask questions to understand motivations
- Value-based selling: Focus on benefits and outcomes
- Emotional selling: Connect to their personal story and meaning
- Social proof: Share examples and testimonials when relevant
- Gentle closing: Guide toward decisions without pressure

OBJECTION HANDLING:
- Acknowledge concerns with empathy
- Provide relevant information and reassurance
- Offer solutions and alternatives
- Focus on value and long-term satisfaction
- Build confidence in their decision

Remember: You're not just selling tattoos, you're helping people bring their personal visions to life while building lasting relationships. Every interaction should leave them feeling heard, valued, and excited about their tattoo journey.
"""
    
    def enhance_rag_response(self, query: str, context: str, base_response: str, 
                           intent: str = None, extracted_info: Dict[str, Any] = None) -> str:
        """Enhance RAG response with sales personality and techniques"""
        
        if not intent:
            intent = self._classify_sales_intent(query)
        
        if not extracted_info:
            extracted_info = self._extract_query_info(query)
        
        # Start building enhanced response
        enhanced_parts = []
        
        # Add appropriate opening based on intent
        opening = self._get_sales_opening(intent, extracted_info)
        if opening:
            enhanced_parts.append(opening)
        
        # Add the base response
        enhanced_parts.append(base_response)
        
        # Add sales-focused enhancement based on intent
        enhancement = self._get_sales_enhancement(intent, extracted_info)
        if enhancement:
            enhanced_parts.append(enhancement)
        
        # Add caring closing
        closing = self._get_sales_closing(intent, extracted_info)
        if closing:
            enhanced_parts.append(closing)
        
        return " ".join(enhanced_parts)
    
    def _get_sales_opening(self, intent: str, extracted_info: Dict[str, Any]) -> str:
        """Get appropriate sales opening based on intent"""
        openings = {
            "pricing": "I completely understand that pricing is important to you. ",
            "scheduling": "I'm excited to help you find the perfect time for your tattoo. ",
            "concerns": "I really appreciate you sharing your concerns with me. ",
            "design": "I love talking about tattoo designs! ",
            "booking": "I'm so excited you're ready to move forward! ",
            "aftercare": "Taking care of your tattoo is so important. ",
            "general_info": "I'm happy to help you with that information. "
        }
        return openings.get(intent, "")
    
    def _get_sales_enhancement(self, intent: str, extracted_info: Dict[str, Any]) -> str:
        """Get sales enhancement based on intent and extracted info"""
        
        if intent == "pricing":
            return " I'd love to work within your budget to create something amazing. We have flexible payment options that might work perfectly for you."
        
        elif intent == "scheduling":
            return " Let's find a time that works perfectly for your schedule. I want to make sure we have enough time to create something you'll absolutely love."
        
        elif intent == "concerns":
            return " I want to make sure you're completely comfortable with this decision. Let me address any concerns you have so you can move forward with confidence."
        
        elif intent == "design":
            return " I'm excited to help bring your vision to life. This is going to be such a meaningful and beautiful piece for you."
        
        elif intent == "booking":
            return " I can't wait to work on this with you. Let's get you scheduled so we can start creating something amazing together."
        
        elif extracted_info.get("experience_level") == "first_time":
            return " I know this might feel like a big step, especially if it's your first tattoo. I'm here to make sure you feel comfortable and confident throughout the entire process."
        
        return ""
    
    def _get_sales_closing(self, intent: str, extracted_info: Dict[str, Any]) -> str:
        """Get appropriate sales closing"""
        
        if intent in ["pricing", "scheduling", "design", "booking"]:
            return " I'm here to answer any other questions you might have and help make this experience amazing for you!"
        
        return " Feel free to ask me anything else - I'm here to help make your tattoo journey as smooth and exciting as possible!"
    
    def create_sales_training_documents(self) -> List[Document]:
        """Create comprehensive sales training documents for RAG system"""
        documents = []
        
        # Sales fundamentals document
        sales_fundamentals = """
# Sales Fundamentals for Tattoo Artists

## Consultative Selling Approach
Building relationships through understanding client needs rather than just pushing products.

### Key Techniques:
1. Ask open-ended questions to understand motivations
2. Listen actively and show genuine interest  
3. Build rapport through shared experiences
4. Focus on client benefits, not just features
5. Create urgency through value proposition

### Value Proposition Framework:
- Professional, licensed artists with years of experience
- Clean, sterile environment following health department standards
- Premium materials and equipment for best results
- Comprehensive aftercare support and follow-up
- Portfolio of excellent work and satisfied clients
- Competitive pricing with flexible payment options

## Emotional Intelligence in Sales
Reading client emotions and responding appropriately:
- Excitement: Match their energy while guiding toward commitment
- Hesitation: Address concerns directly and provide reassurance
- Concern: Show empathy and provide detailed information
- Confidence: Move toward closing and next steps

## Conversation Flow Structure:
1. Opening and rapport building
2. Discovery and needs assessment
3. Value presentation and benefit focus
4. Objection handling with empathy
5. Gentle closing and next steps

## Objection Handling Strategies:
- Price: Focus on value, break down pricing, offer payment plans
- Timing: Show flexibility, create appropriate urgency
- Concerns: Address with empathy, provide information and reassurance

## Closing Techniques:
- Assumptive: "Perfect! Let's get you scheduled..."
- Benefit: "This tattoo will look incredible and you'll love having it..."
- Urgency: "I have a great slot coming up that would be perfect..."

Remember: You're helping people bring their personal visions to life while building lasting relationships.
"""
        
        doc = Document(
            page_content=sales_fundamentals,
            metadata={
                "category": "sales_fundamentals",
                "source": "sales_training",
                "type": "sales_knowledge",
                "personality": "sales_focused_friendly_caring"
            }
        )
        documents.append(doc)
        
        return documents
    
    def save_enhanced_knowledge_base(self, output_path: str):
        """Save enhanced knowledge base with sales integration"""
        enhanced_kb = {
            "sales_personality": {
                "tone": "friendly, caring, and sales-focused",
                "communication_style": "consultative and empathetic",
                "sales_approach": "relationship-building and value-driven",
                "emotional_intelligence": "high - reads client needs and emotions",
                "closing_style": "gentle and assumptive"
            },
            "sales_knowledge": self.sales_knowledge,
            "integration_instructions": {
                "query_enhancement": "Use enhance_query_for_sales() to add sales context",
                "response_enhancement": "Use enhance_rag_response() to add sales personality",
                "personality_prompt": "Use get_sales_personality_prompt() for system messages",
                "document_creation": "Use create_sales_documents() to add to vector store"
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(enhanced_kb, f, indent=2, ensure_ascii=False)
        
        print(f"Enhanced sales knowledge base saved to {output_path}")


# Example usage and testing
if __name__ == "__main__":
    integration = SalesRAGIntegration()
    
    # Test query enhancement
    test_query = "How much would a medium realistic tattoo on my arm cost?"
    enhanced = integration.enhance_query_for_sales(test_query)
    print("Enhanced Query:", enhanced)
    
    # Test response enhancement
    base_response = "Realistic tattoos typically range from $300-$2000 depending on size and complexity."
    enhanced_response = integration.enhance_rag_response(
        test_query, "", base_response, 
        enhanced["intent"], enhanced["extracted_info"]
    )
    print("Enhanced Response:", enhanced_response)
    
    # Create sales documents
    documents = integration.create_sales_documents()
    print(f"Created {len(documents)} sales knowledge documents")
    
    # Save enhanced knowledge base
    integration.save_enhanced_knowledge_base("enhanced_sales_knowledge_base.json")
    
    print("Sales RAG integration completed successfully!")
