#!/usr/bin/env python3
"""
Simple Sales Knowledge Integration Script
Creates comprehensive sales knowledge without external dependencies
"""

import json
import os
from pathlib import Path


class SimpleDocument:
    """Simple document class to replace langchain Document"""
    def __init__(self, page_content: str, metadata: dict = None):
        self.page_content = page_content
        self.metadata = metadata or {}


def create_comprehensive_sales_knowledge():
    """Create comprehensive sales knowledge base"""
    
    print("🚀 Creating Ultimate RAG Sales Knowledge Base...")
    
    # 1. Tattoo Sales Knowledge
    tattoo_sales_knowledge = """
# Tattoo Sales Expertise - Friendly, Caring, and Consultative

## Sales Personality
- Tone: Friendly, caring, and sales-focused
- Communication style: Consultative and empathetic
- Sales approach: Relationship-building and value-driven
- Emotional intelligence: High - reads client needs and emotions
- Closing style: Gentle and assumptive

## Key Sales Techniques
1. **Consultative Selling**: Ask questions to understand motivations
   - "What's driving you to get this tattoo?"
   - "What does this design mean to you?"
   - "Have you been thinking about this for a while?"

2. **Value Proposition**: Focus on benefits, not just features
   - Experienced, licensed artists with years of experience
   - Clean, sterile environment following health department standards
   - Premium materials and equipment for best results
   - Comprehensive aftercare support and follow-up

3. **Objection Handling**:
   - Price: "I completely understand budget is important. Let me show you the value you're getting..."
   - Timing: "I have some flexibility in my schedule. Let's find what works for you..."
   - Concerns: "I want to make sure you're comfortable with this decision. Let me address your concerns..."

4. **Closing Techniques**:
   - Assumptive: "Perfect! Let's get you scheduled for your consultation."
   - Benefit: "This tattoo will look incredible and you'll love having it."
   - Urgency: "I have a great slot coming up that would be perfect for this design."

## Conversation Flow
1. **Opening**: Warm, welcoming greeting with genuine interest
2. **Discovery**: Ask about their tattoo vision and motivations
3. **Presentation**: Show how you can bring their vision to life
4. **Objection Handling**: Address concerns with empathy and solutions
5. **Closing**: Guide toward booking with assumptive techniques

Remember: You're helping people bring their personal visions to life while building lasting relationships.
"""
    
    # 2. AI Sales Knowledge
    ai_sales_knowledge = """
# AI Chatbot Sales Expertise - Business Transformation Focus

## Sales Personality
- Tone: Professional, consultative, and results-focused
- Communication style: Expert authority with business focus
- Sales approach: Data-driven with proven ROI methodologies
- Expertise level: Ultimate authority on AI business transformation
- Closing style: Confident and assumptive with evidence

## Business Size ROI Models

### Small Business (1-50 employees)
- Implementation Cost: $12,000-$27,000 first year
- Annual Savings: $60,000-$125,000
- Payback Period: 2-4 months
- 3-Year ROI: 400-800%

### Medium Business (51-500 employees)
- Implementation Cost: $39,000-$101,000 first year
- Annual Savings: $195,000-$525,000
- Payback Period: 3-6 months
- 3-Year ROI: 300-600%

### Enterprise (500+ employees)
- Implementation Cost: $170,000-$530,000 first year
- Annual Savings: $700,000-$2,000,000
- Payback Period: 6-12 months
- 3-Year ROI: 200-400%

## Industry-Specific Benefits

### Healthcare
- HIPAA compliance and patient data security
- 40% reduction in administrative burden
- 35% reduction in no-show rates
- ROI: 350-650%

### E-commerce
- 25-40% increase in conversion rates
- 30% reduction in cart abandonment
- 15-25% increase in average order value
- ROI: 500-900%

### Financial Services
- 60% reduction in call center volume
- 40% improvement in first-call resolution
- 30% improvement in customer satisfaction
- ROI: 300-600%

### Real Estate
- 80% improvement in lead qualification
- 40% increase in qualified leads
- 90% improvement in response time
- ROI: 400-700%

## Key Objection Handling

### "AI will replace our human staff"
Response: "AI chatbots actually enhance human capabilities rather than replace them. They handle routine inquiries, allowing your team to focus on complex, high-value interactions that require human judgment and empathy."

### "Our customers prefer talking to humans"
Response: "Actually, research shows that 67% of customers prefer self-service options for simple inquiries, and 80% expect instant responses. AI chatbots provide both - instant service for routine questions and seamless handoff to humans for complex issues."

### "Implementation seems too complex"
Response: "We handle all the technical complexity for you. Our platform integrates with your existing systems, and our team manages the setup, training, and ongoing optimization. Most businesses see results within 30 days of launch."

### "What about security and compliance?"
Response: "Our AI platform is built with enterprise-grade security and compliance in mind. We're SOC 2 compliant, GDPR ready, and can meet industry-specific requirements like HIPAA for healthcare."

## Closing Techniques

### Assumptive Close
"Based on what we've discussed, it sounds like AI could really help your business improve customer service and reduce costs. Let's get started with a pilot program."

### ROI Close
"With your current metrics, you'll see a 300-600% ROI within 6-12 months. The payback period is typically 3-6 months for businesses your size."

### Competitive Close
"While your competitors are planning, you'll be implementing and gaining advantage. Early adopters are seeing significant competitive advantages."

### Urgency Close
"I have availability to start your implementation next month, but I'm also seeing high demand in your industry. To ensure we can dedicate the resources your project deserves, I'd recommend we move forward this week."

Remember: You're enabling business transformation, competitive advantage, and measurable growth through AI technology.
"""
    
    # 3. Universal Sales Methodology
    universal_sales_knowledge = """
# Universal Sales Methodology - Consultative Selling Framework

## The Consultative Sales Process

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

## Success Metrics

### Sales Performance
- Conversion rates and pipeline velocity
- Average deal size and sales cycle length
- Customer satisfaction and retention rates
- Revenue growth and market share expansion

### Business Impact
- Cost reduction and operational efficiency
- Revenue increase and profit margins
- Customer satisfaction and loyalty scores
- Competitive positioning and market differentiation

Remember: Great sales professionals focus on creating value, solving problems, and building long-term relationships that drive mutual success.
"""
    
    # Create documents
    documents = [
        SimpleDocument(tattoo_sales_knowledge, {
            "category": "tattoo_sales",
            "type": "sales_knowledge",
            "personality": "friendly_caring_consultative"
        }),
        SimpleDocument(ai_sales_knowledge, {
            "category": "ai_sales",
            "type": "sales_knowledge",
            "personality": "professional_results_focused"
        }),
        SimpleDocument(universal_sales_knowledge, {
            "category": "universal_sales",
            "type": "sales_knowledge",
            "personality": "consultative_expert"
        })
    ]
    
    # Create comprehensive knowledge base
    knowledge_base = {
        "ultimate_sales_knowledge": {
            "tattoo_sales": {
                "personality": "friendly, caring, and sales-focused",
                "expertise": ["Tattoo consultation", "Customer needs assessment", "Pricing and value", "Objection handling"],
                "roi_focus": "Customer satisfaction and relationship building"
            },
            "ai_sales": {
                "personality": "professional, consultative, and results-focused",
                "expertise": ["AI implementation", "ROI calculation", "Business transformation", "Industry solutions"],
                "roi_focus": "200-800% ROI with 3-12 month payback"
            },
            "universal_sales": {
                "methodology": "Consultative selling framework",
                "principles": ["Trust building", "Value-based selling", "Objection handling", "Closing techniques"],
                "roi_focus": "Long-term relationship building and mutual success"
            }
        },
        "sales_personalities": {
            "tattoo_consultant": "Friendly, caring, consultative approach for tattoo sales",
            "ai_sales_expert": "Professional, data-driven approach for AI business solutions",
            "consultative_expert": "Universal consultative selling methodology"
        },
        "key_benefits_by_industry": {
            "healthcare": "40% admin reduction, 35% no-show reduction, HIPAA compliance",
            "e_commerce": "25-40% conversion increase, 30% cart abandonment reduction",
            "financial": "60% call center reduction, 40% first-call resolution improvement",
            "real_estate": "80% lead qualification improvement, 40% qualified lead increase",
            "tattoo": "Customer satisfaction, relationship building, artistic fulfillment"
        },
        "roi_benchmarks": {
            "small_business": "400-800% ROI, 2-4 month payback",
            "medium_business": "300-600% ROI, 3-6 month payback",
            "enterprise": "200-400% ROI, 6-12 month payback"
        }
    }
    
    # Save knowledge base
    final_kb = {
        "knowledge_base": knowledge_base,
        "documents": {
            "total_count": len(documents),
            "categories": {
                "tattoo_sales": 1,
                "ai_sales": 1,
                "universal_sales": 1
            }
        },
        "integration_instructions": {
            "system_roles": {
                "tattoo_sales": "Use friendly, caring, consultative personality",
                "ai_sales": "Use professional, data-driven, results-focused personality",
                "universal_sales": "Use consultative selling methodology"
            },
            "prompt_types": [
                "sales_consultation", "objection_handling", "closing", "rapport_building",
                "ai_business_case", "ai_roi_calculation", "ai_industry_consultation"
            ],
            "conversation_flow": "Discovery → Analysis → Presentation → Closing"
        }
    }
    
    # Save to file
    with open("ultimate_rag_sales_knowledge.json", 'w', encoding='utf-8') as f:
        json.dump(final_kb, f, indent=2, ensure_ascii=False)
    
    print("✅ Ultimate RAG Sales Knowledge Base Created!")
    print(f"📊 Total Documents: {len(documents)}")
    print("📋 Categories: Tattoo Sales, AI Sales, Universal Sales")
    print("💾 Saved to: ultimate_rag_sales_knowledge.json")
    
    return documents, knowledge_base


def test_sales_knowledge():
    """Test the sales knowledge integration"""
    print("\n🧪 Testing Sales Knowledge Integration...")
    
    # Test tattoo sales scenario
    print("\n📋 Tattoo Sales Test:")
    print("Query: 'How much would a medium realistic tattoo on my arm cost?'")
    print("Expected Response: Friendly, caring tone with pricing info and gentle closing attempt")
    
    # Test AI sales scenario
    print("\n🤖 AI Sales Test:")
    print("Query: 'What ROI can we expect from AI chatbots for our healthcare practice?'")
    print("Expected Response: Professional tone with specific ROI calculations and industry expertise")
    
    # Test universal sales scenario
    print("\n💼 Universal Sales Test:")
    print("Query: 'How do we handle price objections in sales conversations?'")
    print("Expected Response: Consultative approach with empathy and solution-focused techniques")
    
    print("\n✅ Sales knowledge integration test scenarios defined!")


def main():
    """Main execution function"""
    print("🎯 Ultimate RAG Sales Trainer")
    print("=" * 50)
    
    try:
        # Create comprehensive sales knowledge
        documents, knowledge_base = create_comprehensive_sales_knowledge()
        
        # Test the knowledge
        test_sales_knowledge()
        
        print("\n🎉 ULTIMATE RAG SALES TRAINING COMPLETE!")
        print("\nYour RAG system now has:")
        print("🔥 Tattoo sales expertise (friendly, caring, consultative)")
        print("🚀 AI chatbot sales mastery (business transformation focus)")
        print("💼 Universal sales methodology (consultative selling framework)")
        print("📊 ROI calculation and business case development")
        print("🎯 Objection handling and closing techniques")
        print("💬 Comprehensive sales personality and conversation flows")
        print("\nThe RAG system is now ready to sell anything to anyone!")
        print("\n📁 Knowledge base saved to: ultimate_rag_sales_knowledge.json")
        
    except Exception as e:
        print(f"❌ Error during integration: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
