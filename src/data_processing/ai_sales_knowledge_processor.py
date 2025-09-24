"""
AI Sales Knowledge Processor
Processes comprehensive AI sales knowledge into the RAG system for enhanced AI sales capabilities
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter


class AISalesKnowledgeProcessor:
    """Processes AI sales knowledge into RAG-ready documents"""
    
    def __init__(self, knowledge_base_path: str = "./ai_sales_knowledge"):
        self.knowledge_base_path = Path(knowledge_base_path)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=300,
            length_function=len
        )
        self.ai_knowledge = self._load_ai_knowledge()
    
    def _load_ai_knowledge(self) -> Dict[str, Any]:
        """Load AI sales knowledge from markdown files"""
        knowledge = {}
        
        if self.knowledge_base_path.exists():
            for file_path in self.knowledge_base_path.glob("*.md"):
                content = file_path.read_text(encoding='utf-8')
                knowledge[file_path.stem] = content
        
        return knowledge
    
    def create_ai_sales_documents(self) -> List[Document]:
        """Create document chunks from AI sales knowledge"""
        documents = []
        
        for category, content in self.ai_knowledge.items():
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
                            "type": "ai_sales_knowledge",
                            "personality": "ai_sales_expert",
                            "domain": self._extract_domain(category, chunk)
                        }
                    )
                    documents.append(doc)
        
        return documents
    
    def _extract_domain(self, category: str, content: str) -> str:
        """Extract domain/industry from content"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['healthcare', 'medical', 'patient', 'hipaa']):
            return 'healthcare'
        elif any(word in content_lower for word in ['e-commerce', 'retail', 'online', 'shopping']):
            return 'e-commerce'
        elif any(word in content_lower for word in ['financial', 'banking', 'finance', 'credit']):
            return 'financial_services'
        elif any(word in content_lower for word in ['real estate', 'property', 'mortgage']):
            return 'real_estate'
        elif any(word in content_lower for word in ['manufacturing', 'b2b', 'industrial']):
            return 'manufacturing'
        elif any(word in content_lower for word in ['roi', 'return', 'investment', 'cost']):
            return 'roi_analysis'
        elif any(word in content_lower for word in ['sales', 'objection', 'closing', 'technique']):
            return 'sales_techniques'
        else:
            return 'general_ai'
    
    def create_ai_sales_personality_prompt(self) -> str:
        """Create comprehensive AI sales personality prompt"""
        return """
You are an AI sales expert and business consultant specializing in AI chatbot solutions for businesses of all sizes. Your expertise makes you the ultimate authority on AI business transformation.

PERSONALITY & APPROACH:
- Professional, consultative, and results-focused
- Deep understanding of AI technology and business applications
- Empathetic to business challenges while maintaining expert authority
- Data-driven approach with proven ROI methodologies
- Confident in AI capabilities while understanding implementation concerns

EXPERTISE DOMAINS:
- AI chatbot implementation across all business sizes (startup to enterprise)
- Industry-specific AI solutions (healthcare, e-commerce, finance, real estate, manufacturing, professional services)
- Comprehensive ROI calculation and business case development
- Advanced objection handling and sales techniques for technology solutions
- Change management, adoption strategies, and implementation best practices
- Competitive analysis and market positioning through AI

SALES METHODOLOGY:
- Consultative selling focused on measurable business outcomes
- Value-based presentations with specific, data-driven ROI calculations
- Industry expertise with relevant case studies and success stories
- Comprehensive objection handling with risk mitigation strategies
- Long-term partnership focus with continuous optimization

CONVERSATION FRAMEWORK:
1. Discovery: Understand business needs, challenges, and objectives
2. Analysis: Assess current state and identify AI opportunities
3. Presentation: Demonstrate specific benefits with ROI calculations
4. Objection Handling: Address concerns with data and evidence
5. Closing: Guide toward business transformation and competitive advantage

KEY SELLING POINTS:
- 24/7 customer service without additional staff costs
- 40-80% reduction in routine customer service tasks
- 25-40% improvement in conversion rates
- 3-12 month payback periods with 200-800% 3-year ROI
- Enterprise-grade security and compliance capabilities
- Seamless integration with existing business systems

INDUSTRY EXPERTISE:
Healthcare: HIPAA compliance, patient communication, appointment scheduling, EMR integration
Financial Services: Regulatory compliance, fraud detection, account management, core banking integration
E-commerce: Conversion optimization, cart abandonment reduction, personalization, multi-channel support
Real Estate: Lead qualification, property information, mortgage support, CRM integration
Manufacturing: Technical support, parts ordering, warranty management, ERP integration
Professional Services: Client onboarding, document management, billing, practice management integration

OBJECTION HANDLING MASTERY:
Technology Concerns: "We handle all technical complexity - you focus on business results"
Budget Constraints: "Typical ROI is 200-800% with 3-12 month payback periods"
Change Management: "We provide comprehensive training and support for smooth adoption"
Security/Compliance: "Enterprise-grade security with industry-specific compliance capabilities"
Implementation Complexity: "Phased approach with proven success and ongoing optimization"

CLOSING TECHNIQUES:
- Assumptive: "Based on your needs, let's start with a pilot program"
- ROI-focused: "With your current metrics, you'll see [specific ROI] within [timeframe]"
- Competitive: "While your competitors are planning, you'll be implementing and gaining advantage"
- Urgency: "Early adopters are gaining significant competitive advantages"

Remember: You're not just selling AI technology - you're enabling business transformation, competitive advantage, and measurable growth. Every conversation should demonstrate deep expertise while building confidence in AI as a strategic business investment.
"""
    
    def create_ai_knowledge_summary(self) -> Dict[str, Any]:
        """Create comprehensive AI knowledge summary"""
        return {
            "ai_sales_expertise": {
                "business_sizes": {
                    "small_business": {
                        "employees": "1-50",
                        "typical_roi": "400-800%",
                        "payback_period": "2-4 months",
                        "cost_reduction": "40-70%",
                        "annual_savings": "$60,000-$125,000"
                    },
                    "medium_business": {
                        "employees": "51-500",
                        "typical_roi": "300-600%",
                        "payback_period": "3-6 months",
                        "cost_reduction": "50-80%",
                        "annual_savings": "$195,000-$525,000"
                    },
                    "enterprise": {
                        "employees": "500+",
                        "typical_roi": "200-400%",
                        "payback_period": "6-12 months",
                        "cost_reduction": "60-85%",
                        "annual_savings": "$700,000-$2,000,000"
                    }
                },
                "industry_benefits": {
                    "healthcare": {
                        "key_benefits": ["HIPAA compliance", "40% administrative reduction", "35% no-show reduction"],
                        "use_cases": ["appointment scheduling", "patient communication", "insurance verification"],
                        "roi": "350-650%"
                    },
                    "e_commerce": {
                        "key_benefits": ["25-40% conversion increase", "30% cart abandonment reduction", "15-25% AOV increase"],
                        "use_cases": ["product recommendations", "order tracking", "customer support"],
                        "roi": "500-900%"
                    },
                    "financial_services": {
                        "key_benefits": ["60% call center reduction", "40% first-call resolution", "30% customer satisfaction"],
                        "use_cases": ["account inquiries", "fraud detection", "loan applications"],
                        "roi": "300-600%"
                    },
                    "real_estate": {
                        "key_benefits": ["80% lead qualification improvement", "40% response time", "40% qualified leads"],
                        "use_cases": ["lead qualification", "property information", "appointment scheduling"],
                        "roi": "400-700%"
                    }
                },
                "common_objections": {
                    "technology_complexity": "We handle all technical complexity - you focus on business results",
                    "budget_constraints": "Typical ROI is 200-800% with 3-12 month payback periods",
                    "change_management": "Comprehensive training and support for smooth adoption",
                    "security_compliance": "Enterprise-grade security with industry-specific compliance",
                    "implementation_fears": "Phased approach with proven success and ongoing optimization"
                },
                "success_metrics": {
                    "operational": ["<1 second response time", "99.9% uptime", "70-85% resolution rate"],
                    "business": ["20-40% conversion improvement", "15-30% retention improvement", "10-25% AOV increase"],
                    "financial": ["$0.10-$0.50 per interaction", "3-12 month payback", "200-800% 3-year ROI"]
                }
            }
        }
    
    def enhance_query_for_ai_sales(self, query: str) -> Dict[str, Any]:
        """Enhance query with AI sales context and classification"""
        
        # Classify query intent
        intent = self._classify_ai_sales_intent(query)
        
        # Extract business information
        business_info = self._extract_business_info(query)
        
        # Generate AI sales context
        ai_context = self._generate_ai_sales_context(intent, business_info)
        
        return {
            "original_query": query,
            "intent": intent,
            "business_info": business_info,
            "ai_context": ai_context,
            "enhanced_query": f"{query} [AI Sales Context: {ai_context}]"
        }
    
    def _classify_ai_sales_intent(self, query: str) -> str:
        """Classify the AI sales intent of the query"""
        query_lower = query.lower()
        
        intent_patterns = {
            "roi_calculation": ["roi", "return on investment", "cost", "savings", "payback", "benefit"],
            "business_case": ["business case", "justification", "investment", "proposal", "presentation"],
            "industry_solution": ["industry", "healthcare", "finance", "retail", "manufacturing", "real estate"],
            "objection_handling": ["concern", "worry", "problem", "issue", "risk", "hesitation"],
            "implementation": ["implement", "setup", "deploy", "install", "rollout", "launch"],
            "feature_questions": ["feature", "capability", "function", "what can", "how does"],
            "pricing": ["price", "cost", "expensive", "budget", "afford"],
            "competition": ["competitor", "alternative", "compare", "better than", "vs"],
            "general_info": ["what is", "tell me", "explain", "information", "about"]
        }
        
        for intent, patterns in intent_patterns.items():
            if any(pattern in query_lower for pattern in patterns):
                return intent
        
        return "general_info"
    
    def _extract_business_info(self, query: str) -> Dict[str, Any]:
        """Extract business information from query"""
        query_lower = query.lower()
        
        extracted = {
            "company_size": None,
            "industry": None,
            "revenue_range": None,
            "current_challenge": None,
            "budget_mentioned": False
        }
        
        # Extract company size
        if any(word in query_lower for word in ["small", "startup", "local"]):
            extracted["company_size"] = "small"
        elif any(word in query_lower for word in ["medium", "mid-size", "regional"]):
            extracted["company_size"] = "medium"
        elif any(word in query_lower for word in ["enterprise", "large", "corporate", "fortune"]):
            extracted["company_size"] = "enterprise"
        
        # Extract industry
        industries = ["healthcare", "medical", "finance", "banking", "retail", "e-commerce", "manufacturing", "real estate", "legal", "accounting"]
        for industry in industries:
            if industry in query_lower:
                extracted["industry"] = industry
                break
        
        # Check for budget mention
        budget_words = ["budget", "cost", "expensive", "afford", "price"]
        extracted["budget_mentioned"] = any(word in query_lower for word in budget_words)
        
        return extracted
    
    def _generate_ai_sales_context(self, intent: str, business_info: Dict[str, Any]) -> str:
        """Generate AI sales context based on intent and business info"""
        context_parts = []
        
        # Add intent-based context
        if intent == "roi_calculation":
            context_parts.append("Focus on specific ROI calculations and business case development")
        elif intent == "business_case":
            context_parts.append("Develop comprehensive business case with executive summary and financial analysis")
        elif intent == "industry_solution":
            context_parts.append("Provide industry-specific AI solutions and use cases")
        elif intent == "objection_handling":
            context_parts.append("Address concerns with empathy and data-driven responses")
        elif intent == "implementation":
            context_parts.append("Detail implementation roadmap and change management strategies")
        
        # Add business info context
        if business_info["company_size"]:
            context_parts.append(f"Company size: {business_info['company_size']}")
        
        if business_info["industry"]:
            context_parts.append(f"Industry: {business_info['industry']}")
        
        if business_info["budget_mentioned"]:
            context_parts.append("Budget-sensitive - focus on value and ROI")
        
        return " | ".join(context_parts)
    
    def save_ai_knowledge_base(self, output_path: str):
        """Save processed AI knowledge base"""
        ai_kb = {
            "ai_sales_personality": self.create_ai_sales_personality_prompt(),
            "knowledge_summary": self.create_ai_knowledge_summary(),
            "integration_instructions": {
                "personality_role": "Use 'ai_sales_expert' system role for AI sales conversations",
                "prompt_types": ["ai_business_case", "ai_roi_calculation", "ai_industry_consultation"],
                "query_enhancement": "Use enhance_query_for_ai_sales() to add AI sales context",
                "document_creation": "Use create_ai_sales_documents() to add to vector store"
            },
            "knowledge_categories": list(self.ai_knowledge.keys())
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(ai_kb, f, indent=2, ensure_ascii=False)
        
        print(f"AI sales knowledge base saved to {output_path}")


# Example usage and testing
if __name__ == "__main__":
    processor = AISalesKnowledgeProcessor()
    
    # Test query enhancement
    test_query = "How much ROI can we expect from AI chatbots for our healthcare practice?"
    enhanced = processor.enhance_query_for_ai_sales(test_query)
    print("Enhanced Query:", enhanced)
    
    # Create AI sales documents
    documents = processor.create_ai_sales_documents()
    print(f"Created {len(documents)} AI sales knowledge documents")
    
    # Save AI knowledge base
    processor.save_ai_knowledge_base("ai_sales_knowledge_base.json")
    
    print("AI sales knowledge processing completed successfully!")
