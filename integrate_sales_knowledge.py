#!/usr/bin/env python3
"""
Ultimate RAG Sales Knowledge Integration Script
Integrates comprehensive sales knowledge (tattoo + AI chatbot) into the RAG system
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent / "src"))

from data_processing.sales_knowledge_enhancer import SalesKnowledgeEnhancer
from data_processing.ai_sales_knowledge_processor import AISalesKnowledgeProcessor
from data_processing.document_processor import DocumentProcessor


class UltimateRAGSalesTrainer:
    """Ultimate RAG Sales Trainer - Integrates comprehensive sales knowledge"""
    
    def __init__(self):
        self.sales_enhancer = SalesKnowledgeEnhancer()
        self.ai_processor = AISalesKnowledgeProcessor()
        self.document_processor = DocumentProcessor()
        
    def integrate_all_sales_knowledge(self):
        """Integrate all sales knowledge into the RAG system"""
        print("🚀 Starting Ultimate RAG Sales Knowledge Integration...")
        
        # 1. Process tattoo sales knowledge
        print("\n📋 Processing Tattoo Sales Knowledge...")
        tattoo_docs = self.sales_enhancer.create_sales_training_documents()
        print(f"✅ Created {len(tattoo_docs)} tattoo sales documents")
        
        # 2. Process AI sales knowledge
        print("\n🤖 Processing AI Sales Knowledge...")
        ai_docs = self.ai_processor.create_ai_sales_documents()
        print(f"✅ Created {len(ai_docs)} AI sales documents")
        
        # 3. Process additional sales knowledge documents
        print("\n📚 Processing Additional Sales Documents...")
        additional_docs = self._process_additional_sales_documents()
        print(f"✅ Created {len(additional_docs)} additional sales documents")
        
        # 4. Combine all documents
        all_documents = tattoo_docs + ai_docs + additional_docs
        print(f"\n📊 Total Documents Created: {len(all_documents)}")
        
        # 5. Create comprehensive knowledge base
        print("\n💾 Creating Comprehensive Knowledge Base...")
        knowledge_base = self._create_comprehensive_knowledge_base()
        
        # 6. Save everything
        print("\n💾 Saving Knowledge Base...")
        self._save_knowledge_base(all_documents, knowledge_base)
        
        print("\n🎉 Ultimate RAG Sales Knowledge Integration Complete!")
        print("\n📈 The RAG system is now equipped with:")
        print("   ✅ Tattoo sales expertise (friendly, caring, consultative)")
        print("   ✅ AI chatbot sales mastery (business transformation focus)")
        print("   ✅ Industry-specific knowledge (healthcare, e-commerce, finance, etc.)")
        print("   ✅ ROI calculation and business case development")
        print("   ✅ Objection handling and closing techniques")
        print("   ✅ Comprehensive sales personality and conversation flows")
        
        return all_documents, knowledge_base
    
    def _process_additional_sales_documents(self) -> List[Any]:
        """Process additional sales knowledge documents"""
        documents = []
        
        # Create comprehensive sales methodology document
        sales_methodology = """
# Ultimate Sales Methodology for RAG System

## The Consultative Sales Framework

### 1. Discovery Phase
- Understand client needs and pain points
- Identify decision-making process and stakeholders
- Assess budget and timeline constraints
- Explore current challenges and desired outcomes

### 2. Analysis Phase
- Analyze current state and identify opportunities
- Develop value proposition and ROI projections
- Create tailored solution recommendations
- Address potential objections and concerns

### 3. Presentation Phase
- Present customized solution with clear benefits
- Demonstrate ROI and business case
- Show relevant case studies and success stories
- Address concerns and provide reassurance

### 4. Closing Phase
- Guide toward decision with assumptive techniques
- Create appropriate urgency and next steps
- Overcome final objections and concerns
- Secure commitment and implementation planning

## Universal Sales Principles

### Building Trust and Rapport
- Listen actively and show genuine interest
- Ask thoughtful questions about their business
- Share relevant experiences and insights
- Be transparent about capabilities and limitations

### Value-Based Selling
- Focus on outcomes, not features
- Quantify benefits with specific metrics
- Address ROI and business impact
- Demonstrate competitive advantages

### Objection Handling Mastery
- Acknowledge concerns with empathy
- Provide relevant information and solutions
- Address root causes, not just symptoms
- Guide toward positive resolution

### Closing Techniques
- Use assumptive language appropriately
- Create genuine urgency when relevant
- Focus on benefits and positive outcomes
- Guide toward next steps and commitment

## Industry Expertise Framework

### Healthcare Sales Approach
- Emphasize compliance and patient safety
- Focus on administrative efficiency and patient satisfaction
- Address HIPAA and regulatory requirements
- Demonstrate ROI through reduced overhead and improved care

### Technology Sales Approach
- Highlight innovation and competitive advantage
- Address implementation complexity and support
- Focus on scalability and future-proofing
- Demonstrate measurable business transformation

### Service Industry Sales Approach
- Emphasize customer experience and satisfaction
- Focus on operational efficiency and cost reduction
- Address staff productivity and job satisfaction
- Demonstrate value through improved service delivery

## Success Metrics and KPIs

### Sales Performance Metrics
- Conversion rates and pipeline velocity
- Average deal size and sales cycle length
- Customer satisfaction and retention rates
- Revenue growth and market share expansion

### Business Impact Metrics
- Cost reduction and operational efficiency
- Revenue increase and profit margins
- Customer satisfaction and loyalty scores
- Competitive positioning and market differentiation

Remember: Great sales professionals focus on creating value, solving problems, and building long-term relationships that drive mutual success.
"""
        
        from langchain.schema import Document
        doc = Document(
            page_content=sales_methodology,
            metadata={
                "category": "sales_methodology",
                "source": "ultimate_sales_training",
                "type": "sales_knowledge",
                "personality": "consultative_sales_expert"
            }
        )
        documents.append(doc)
        
        return documents
    
    def _create_comprehensive_knowledge_base(self) -> Dict[str, Any]:
        """Create comprehensive knowledge base combining all sales expertise"""
        
        return {
            "ultimate_sales_knowledge": {
                "tattoo_sales": {
                    "personality": {
                        "tone": "friendly, caring, and sales-focused",
                        "communication_style": "consultative and empathetic",
                        "sales_approach": "relationship-building and value-driven",
                        "emotional_intelligence": "high - reads client needs and emotions",
                        "closing_style": "gentle and assumptive"
                    },
                    "expertise_areas": [
                        "Tattoo styles and techniques",
                        "Customer consultation and needs assessment",
                        "Pricing and value proposition",
                        "Aftercare and customer support",
                        "Objection handling and closing"
                    ]
                },
                "ai_sales": {
                    "personality": {
                        "tone": "professional, consultative, and results-focused",
                        "communication_style": "expert authority with business focus",
                        "sales_approach": "data-driven with proven ROI methodologies",
                        "expertise_level": "ultimate authority on AI business transformation",
                        "closing_style": "confident and assumptive with evidence"
                    },
                    "expertise_areas": [
                        "AI chatbot implementation for all business sizes",
                        "Industry-specific AI solutions and use cases",
                        "ROI calculation and business case development",
                        "Objection handling for technology solutions",
                        "Change management and implementation strategies"
                    ]
                },
                "universal_sales": {
                    "methodology": "Consultative selling framework",
                    "principles": [
                        "Build trust and rapport through genuine interest",
                        "Focus on value and outcomes, not just features",
                        "Handle objections with empathy and solutions",
                        "Close with assumptive techniques and next steps"
                    ],
                    "industries": [
                        "Healthcare", "Technology", "Financial Services",
                        "E-commerce", "Real Estate", "Manufacturing",
                        "Professional Services", "Tattoo and Body Art"
                    ]
                }
            },
            "sales_personalities": {
                "tattoo_consultant": "Use 'sales_consultant' system role for tattoo sales",
                "ai_sales_expert": "Use 'ai_sales_expert' system role for AI chatbot sales",
                "consultative_expert": "Use 'expert' system role for general sales expertise"
            },
            "prompt_types": {
                "sales_focused": [
                    "sales_consultation", "objection_handling", "closing", "rapport_building"
                ],
                "ai_focused": [
                    "ai_business_case", "ai_roi_calculation", "ai_industry_consultation"
                ],
                "general_sales": [
                    "qa", "analysis", "conversation"
                ]
            }
        }
    
    def _save_knowledge_base(self, documents: List[Any], knowledge_base: Dict[str, Any]):
        """Save the comprehensive knowledge base"""
        
        # Save documents metadata
        docs_metadata = []
        for doc in documents:
            docs_metadata.append({
                "content_preview": doc.page_content[:200] + "...",
                "metadata": doc.metadata,
                "category": doc.metadata.get("category", "unknown"),
                "type": doc.metadata.get("type", "unknown")
            })
        
        # Create final knowledge base
        final_kb = {
            "knowledge_base": knowledge_base,
            "documents": {
                "total_count": len(documents),
                "categories": {
                    "tattoo_sales": len([d for d in docs_metadata if "tattoo" in d["category"].lower()]),
                    "ai_sales": len([d for d in docs_metadata if "ai" in d["category"].lower()]),
                    "sales_methodology": len([d for d in docs_metadata if "sales" in d["category"].lower()])
                },
                "document_list": docs_metadata
            },
            "integration_instructions": {
                "rag_system": "Use these documents to enhance RAG responses with sales expertise",
                "prompt_manager": "Use the specified prompt types for different sales scenarios",
                "system_roles": "Use the specified system roles for different sales personalities",
                "query_enhancement": "Enhance queries with sales context before processing"
            }
        }
        
        # Save to file
        with open("ultimate_rag_sales_knowledge.json", 'w', encoding='utf-8') as f:
            json.dump(final_kb, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Knowledge base saved to ultimate_rag_sales_knowledge.json")
        
        # Also save individual knowledge bases
        self.sales_enhancer.save_knowledge_base("tattoo_sales_knowledge.json")
        self.ai_processor.save_ai_knowledge_base("ai_sales_knowledge.json")
        
        print("✅ Individual knowledge bases saved")
    
    def test_sales_knowledge_integration(self):
        """Test the integrated sales knowledge"""
        print("\n🧪 Testing Sales Knowledge Integration...")
        
        # Test tattoo sales knowledge
        print("\n📋 Testing Tattoo Sales Knowledge:")
        test_query = "How much would a medium realistic tattoo on my arm cost?"
        enhanced = self.sales_enhancer.enhance_rag_response(
            test_query, "", "Realistic tattoos typically range from $300-$2000 depending on size and complexity."
        )
        print(f"Enhanced Response: {enhanced[:100]}...")
        
        # Test AI sales knowledge
        print("\n🤖 Testing AI Sales Knowledge:")
        ai_enhanced = self.ai_processor.enhance_query_for_ai_sales(
            "What ROI can we expect from AI chatbots for our healthcare practice?"
        )
        print(f"AI Enhanced Query: {ai_enhanced['ai_context']}")
        
        print("\n✅ Sales knowledge integration test completed successfully!")


def main():
    """Main execution function"""
    print("🎯 Ultimate RAG Sales Trainer")
    print("=" * 50)
    
    trainer = UltimateRAGSalesTrainer()
    
    try:
        # Integrate all sales knowledge
        documents, knowledge_base = trainer.integrate_all_sales_knowledge()
        
        # Test the integration
        trainer.test_sales_knowledge_integration()
        
        print("\n🎉 ULTIMATE RAG SALES TRAINING COMPLETE!")
        print("\nYour RAG system now has:")
        print("🔥 Tattoo sales expertise (friendly, caring, consultative)")
        print("🚀 AI chatbot sales mastery (business transformation focus)")
        print("💼 Industry-specific knowledge across all major sectors")
        print("📊 ROI calculation and business case development")
        print("🎯 Objection handling and closing techniques")
        print("💬 Comprehensive sales personality and conversation flows")
        print("\nThe RAG system is now ready to sell anything to anyone!")
        
    except Exception as e:
        print(f"❌ Error during integration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
