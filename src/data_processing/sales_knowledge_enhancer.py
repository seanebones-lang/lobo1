"""
Sales Knowledge Enhancer for RAG System
Enhances the RAG system with comprehensive sales knowledge and personality
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SalesPersonality:
    """Sales-focused personality configuration"""
    tone: str = "friendly, caring, and sales-focused"
    communication_style: str = "consultative and empathetic"
    sales_approach: str = "relationship-building and value-driven"
    emotional_intelligence: str = "high - reads client needs and emotions"
    closing_style: str = "gentle and assumptive"


class SalesKnowledgeEnhancer:
    """Enhances RAG system with comprehensive sales knowledge"""
    
    def __init__(self):
        self.sales_personality = SalesPersonality()
        self.sales_knowledge = self._initialize_sales_knowledge()
        self.conversation_patterns = self._initialize_conversation_patterns()
        self.objection_handling = self._initialize_objection_handling()
        self.closing_techniques = self._initialize_closing_techniques()
    
    def _initialize_sales_knowledge(self) -> Dict[str, Any]:
        """Initialize comprehensive sales knowledge base"""
        return {
            "sales_fundamentals": {
                "consultative_selling": {
                    "description": "Building relationships through understanding client needs",
                    "techniques": [
                        "Ask open-ended questions to understand motivations",
                        "Listen actively and show genuine interest",
                        "Build rapport through shared experiences",
                        "Focus on client benefits, not just features",
                        "Create urgency through value proposition"
                    ],
                    "questions": [
                        "What's driving you to get this tattoo?",
                        "What does this design mean to you?",
                        "Have you been thinking about this for a while?",
                        "What's your timeline for getting this done?",
                        "What concerns do you have about the process?"
                    ]
                },
                "value_proposition": {
                    "core_values": [
                        "Professional, licensed artists with years of experience",
                        "Clean, sterile environment following health department standards",
                        "Premium materials and equipment for best results",
                        "Comprehensive aftercare support and follow-up",
                        "Portfolio of exceptional work and satisfied clients",
                        "Competitive pricing with flexible payment options"
                    ],
                    "differentiators": [
                        "Custom design consultation included",
                        "Lifetime touch-up guarantee on quality work",
                        "Flexible scheduling to accommodate client needs",
                        "Transparent pricing with no hidden fees",
                        "Personalized aftercare guidance"
                    ]
                }
            },
            
            "emotional_intelligence": {
                "reading_clients": {
                    "indicators": {
                        "excitement": ["Rapid speech", "Bright eyes", "Forward lean", "Smiling frequently"],
                        "hesitation": ["Crossed arms", "Stepped back", "Avoiding eye contact", "Long pauses"],
                        "concern": ["Frowning", "Touching face", "Shifting weight", "Asking many questions"],
                        "confidence": ["Direct eye contact", "Upright posture", "Clear speech", "Firm handshake"]
                    },
                    "responses": {
                        "excitement": "Match their energy and enthusiasm while guiding toward commitment",
                        "hesitation": "Address concerns directly and provide reassurance",
                        "concern": "Show empathy and provide detailed information",
                        "confidence": "Move toward closing and next steps"
                    }
                },
                "emotional_triggers": {
                    "positive": ["Achievement", "Self-expression", "Memorial tribute", "Personal growth"],
                    "concerns": ["Pain", "Cost", "Permanence", "Social acceptance", "Professional impact"]
                }
            },
            
            "conversation_flow": {
                "opening": {
                    "greeting": [
                        "Welcome! I'm so excited to meet you and hear about your tattoo vision.",
                        "Hi there! Thanks for coming in today. What brings you in?",
                        "Welcome to our shop! I can already tell you have something special in mind."
                    ],
                    "rapport_building": [
                        "How did you hear about our shop?",
                        "Have you had tattoos before, or is this your first?",
                        "What's the story behind this design idea?",
                        "Are you excited about getting started?"
                    ]
                },
                "discovery": {
                    "needs_assessment": [
                        "Tell me about the design you have in mind.",
                        "What's driving you to get this tattoo?",
                        "What does this tattoo mean to you?",
                        "Have you been thinking about this for a while?",
                        "What's your ideal timeline for getting this done?"
                    ],
                    "budget_exploration": [
                        "Do you have a budget range in mind for this piece?",
                        "Are you looking for something simple or more detailed?",
                        "Would you prefer to do this in one session or spread it out?",
                        "Are you open to discussing payment options?"
                    ]
                },
                "presentation": {
                    "benefit_focused": [
                        "This design will look amazing on you because...",
                        "What I love about this concept is how it will...",
                        "This placement will really showcase the detail because...",
                        "The color scheme will complement your skin tone perfectly..."
                    ],
                    "social_proof": [
                        "I just finished a similar piece last week, and the client was thrilled.",
                        "This style is very popular right now, and for good reason.",
                        "I've done over 50 pieces in this style, and each one is unique.",
                        "Let me show you some examples from my portfolio."
                    ]
                }
            },
            
            "objection_handling": {
                "price_objections": {
                    "responses": [
                        "I completely understand budget is important. Let me break down the value you're getting...",
                        "I want to make sure you get exactly what you want within your budget. Let's explore options...",
                        "The price reflects the quality and experience you'll receive. Let me show you why...",
                        "I have flexible payment options that might work better for you..."
                    ],
                    "techniques": [
                        "Break down pricing by component (design, time, materials)",
                        "Compare to other shops and highlight differences",
                        "Offer payment plans or partial payment options",
                        "Emphasize long-term value and quality"
                    ]
                },
                "timing_objections": {
                    "responses": [
                        "I understand timing is important. Let me check what works for your schedule...",
                        "We can definitely work with your timeline. Let me see what's available...",
                        "I want to make sure we have enough time to do this right. Let's plan it properly...",
                        "I have some flexibility in my schedule. What works best for you?"
                    ],
                    "techniques": [
                        "Show availability and create urgency for good slots",
                        "Explain why proper timing leads to better results",
                        "Offer consultation first to lock in the design",
                        "Create excitement about the process"
                    ]
                },
                "concern_objections": {
                    "pain_concerns": [
                        "I understand your concern about pain. Let me explain what to expect...",
                        "Pain is different for everyone, but I'll make sure you're comfortable...",
                        "I use techniques to minimize discomfort, and we can take breaks as needed...",
                        "Most clients say it's much better than they expected. Let me show you how I help..."
                    ],
                    "permanence_concerns": [
                        "I completely understand this is a big decision. Let's make sure you love the design...",
                        "That's exactly why we do a thorough consultation first...",
                        "I want you to be 100% confident in this decision. Let's take our time...",
                        "The design process ensures you'll love it before we start..."
                    ]
                }
            },
            
            "closing_techniques": {
                "assumptive_close": [
                    "Perfect! Let's get you scheduled for your consultation.",
                    "Great! I'll get the paperwork started for your appointment.",
                    "Excellent choice! When would you like to come in for your consultation?",
                    "I'm excited to work on this with you. Let's get it scheduled."
                ],
                "urgency_close": [
                    "I have a great slot next week that would be perfect for this design.",
                    "I'm booking up quickly, but I'd love to save you a spot.",
                    "This design would look amazing, and I have availability coming up.",
                    "Let's lock in a date so we can get started on your vision."
                ],
                "benefit_close": [
                    "This tattoo will look incredible and you'll love having it.",
                    "You're going to be so happy with how this turns out.",
                    "This is going to be a beautiful piece that you'll cherish.",
                    "I can't wait to see your reaction when it's finished."
                ]
            },
            
            "follow_up_strategies": {
                "immediate": [
                    "Send confirmation details and preparation instructions",
                    "Share portfolio examples of similar work",
                    "Provide contact information for questions",
                    "Set expectations for the process"
                ],
                "pre_appointment": [
                    "Check in 24-48 hours before appointment",
                    "Confirm design and placement",
                    "Remind about preparation steps",
                    "Address any last-minute questions"
                ],
                "post_appointment": [
                    "Follow up within 24 hours to check healing",
                    "Provide aftercare reminders",
                    "Schedule follow-up photos",
                    "Ask for feedback and reviews"
                ],
                "long_term": [
                    "Send birthday and holiday messages",
                    "Share new work and promotions",
                    "Request referrals from satisfied clients",
                    "Maintain relationship through social media"
                ]
            }
        }
    
    def _initialize_conversation_patterns(self) -> Dict[str, List[str]]:
        """Initialize conversation patterns for sales interactions"""
        return {
            "opening_patterns": [
                "I'm so excited to help you bring your tattoo vision to life!",
                "Welcome! I can tell you have something special in mind.",
                "Hi there! Thanks for coming in. I'd love to hear about your tattoo idea.",
                "Welcome to our shop! What brings you in today?"
            ],
            
            "rapport_building": [
                "How did you hear about our shop?",
                "Have you had tattoos before, or is this your first?",
                "What's the story behind this design idea?",
                "Are you excited about getting started?",
                "What's driving you to get this tattoo?"
            ],
            
            "needs_discovery": [
                "Tell me about the design you have in mind.",
                "What does this tattoo mean to you?",
                "Have you been thinking about this for a while?",
                "What's your ideal timeline for getting this done?",
                "Do you have a budget range in mind for this piece?"
            ],
            
            "value_presentation": [
                "This design will look amazing on you because...",
                "What I love about this concept is how it will...",
                "This placement will really showcase the detail because...",
                "The color scheme will complement your skin tone perfectly...",
                "I just finished a similar piece last week, and the client was thrilled."
            ],
            
            "objection_handling": [
                "I completely understand your concern. Let me address that...",
                "That's a great question. Here's what I can tell you...",
                "I want to make sure you're comfortable with this decision...",
                "Let me explain why this is such a great choice...",
                "I have some options that might work better for you..."
            ],
            
            "closing_attempts": [
                "Perfect! Let's get you scheduled for your consultation.",
                "Great! I'll get the paperwork started for your appointment.",
                "Excellent choice! When would you like to come in?",
                "I'm excited to work on this with you. Let's get it scheduled.",
                "This is going to be a beautiful piece. Let's make it happen!"
            ]
        }
    
    def _initialize_objection_handling(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize objection handling responses"""
        return {
            "price": {
                "acknowledgment": [
                    "I completely understand budget is important.",
                    "I want to make sure you get great value for your investment.",
                    "Let me show you what you're getting for this price.",
                    "I have some options that might work better for your budget."
                ],
                "response": [
                    "The price reflects the quality and experience you'll receive.",
                    "Let me break down the value you're getting...",
                    "I have flexible payment options that might work better for you.",
                    "This is an investment in something you'll have for life."
                ],
                "close": [
                    "I want to make this work for you. What feels comfortable?",
                    "Let's find a solution that works for your budget.",
                    "I'm confident we can create something amazing within your range.",
                    "What if we could make this happen within your budget?"
                ]
            },
            
            "timing": {
                "acknowledgment": [
                    "I understand timing is important to you.",
                    "Let me work with your schedule.",
                    "I want to make sure we have enough time to do this right.",
                    "Your timeline is important to me."
                ],
                "response": [
                    "I have some flexibility in my schedule.",
                    "Let me check what works for your availability.",
                    "We can definitely work with your timeline.",
                    "I want to make sure we plan this properly."
                ],
                "close": [
                    "What timeframe works best for you?",
                    "Let's find a time that works for both of us.",
                    "I can work with your schedule. What's your preference?",
                    "When would you like to get started?"
                ]
            },
            
            "concerns": {
                "acknowledgment": [
                    "I completely understand your concern.",
                    "That's a very valid question.",
                    "I want to make sure you're comfortable with this decision.",
                    "Let me address that concern for you."
                ],
                "response": [
                    "Here's what I can tell you about that...",
                    "Let me explain what to expect...",
                    "I've dealt with this concern before, and here's how I help...",
                    "That's exactly why we do a thorough consultation first."
                ],
                "close": [
                    "Does that help address your concern?",
                    "Are you feeling more comfortable with the process now?",
                    "What other questions do you have?",
                    "Is there anything else I can clarify for you?"
                ]
            }
        }
    
    def _initialize_closing_techniques(self) -> Dict[str, List[str]]:
        """Initialize closing techniques"""
        return {
            "assumptive": [
                "Perfect! Let's get you scheduled for your consultation.",
                "Great! I'll get the paperwork started for your appointment.",
                "Excellent choice! When would you like to come in for your consultation?",
                "I'm excited to work on this with you. Let's get it scheduled."
            ],
            
            "urgency": [
                "I have a great slot next week that would be perfect for this design.",
                "I'm booking up quickly, but I'd love to save you a spot.",
                "This design would look amazing, and I have availability coming up.",
                "Let's lock in a date so we can get started on your vision."
            ],
            
            "benefit": [
                "This tattoo will look incredible and you'll love having it.",
                "You're going to be so happy with how this turns out.",
                "This is going to be a beautiful piece that you'll cherish.",
                "I can't wait to see your reaction when it's finished."
            ],
            
            "trial": [
                "What if we started with a consultation to finalize the design?",
                "Would you like to see some examples of similar work I've done?",
                "How about we schedule a design session to work out the details?",
                "What if I could show you exactly how this would look on you?"
            ],
            
            "alternative": [
                "We could start with a smaller version to see how you like it.",
                "What if we did this in stages to spread out the cost?",
                "I could create a few design options for you to choose from.",
                "We could schedule a consultation first to make sure it's perfect."
            ]
        }
    
    def enhance_rag_response(self, query: str, context: str, base_response: str) -> str:
        """Enhance RAG response with sales knowledge and personality"""
        
        # Determine the type of interaction
        interaction_type = self._classify_interaction(query)
        
        # Apply sales personality and knowledge
        enhanced_response = self._apply_sales_enhancement(
            query, context, base_response, interaction_type
        )
        
        return enhanced_response
    
    def _classify_interaction(self, query: str) -> str:
        """Classify the type of sales interaction"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['price', 'cost', 'expensive', 'budget']):
            return 'pricing'
        elif any(word in query_lower for word in ['when', 'time', 'schedule', 'appointment']):
            return 'scheduling'
        elif any(word in query_lower for word in ['pain', 'hurt', 'uncomfortable', 'worried']):
            return 'concerns'
        elif any(word in query_lower for word in ['design', 'style', 'idea', 'concept']):
            return 'design_discussion'
        elif any(word in query_lower for word in ['book', 'schedule', 'appointment', 'consultation']):
            return 'booking'
        else:
            return 'general'
    
    def _apply_sales_enhancement(self, query: str, context: str, base_response: str, interaction_type: str) -> str:
        """Apply sales enhancement based on interaction type"""
        
        # Start with friendly, caring tone
        enhanced_parts = []
        
        # Add appropriate opening based on interaction type
        if interaction_type == 'pricing':
            enhanced_parts.append("I completely understand that pricing is important to you. ")
            enhanced_parts.append(self._get_objection_response('price', 'acknowledgment'))
        elif interaction_type == 'scheduling':
            enhanced_parts.append("I'm excited to help you find the perfect time for your tattoo. ")
        elif interaction_type == 'concerns':
            enhanced_parts.append("I really appreciate you sharing your concerns with me. ")
        elif interaction_type == 'design_discussion':
            enhanced_parts.append("I love talking about tattoo designs! ")
        elif interaction_type == 'booking':
            enhanced_parts.append("I'm so excited you're ready to move forward! ")
        
        # Add the base response
        enhanced_parts.append(base_response)
        
        # Add sales-focused closing
        if interaction_type in ['pricing', 'scheduling', 'design_discussion']:
            enhanced_parts.append(self._get_closing_attempt(interaction_type))
        
        # Add caring follow-up
        enhanced_parts.append(" I'm here to answer any other questions you might have and help make this experience amazing for you!")
        
        return "".join(enhanced_parts)
    
    def _get_objection_response(self, objection_type: str, response_type: str) -> str:
        """Get objection handling response"""
        if objection_type in self.objection_handling and response_type in self.objection_handling[objection_type]:
            responses = self.objection_handling[objection_type][response_type]
            return responses[0] if responses else ""
        return ""
    
    def _get_closing_attempt(self, interaction_type: str) -> str:
        """Get appropriate closing attempt"""
        if interaction_type == 'pricing':
            return " I'd love to work within your budget to create something amazing. "
        elif interaction_type == 'scheduling':
            return " Let's find a time that works perfectly for you. "
        elif interaction_type == 'design_discussion':
            return " I'm excited to help bring your vision to life. "
        else:
            return " I'm here to help make this happen for you. "
    
    def get_sales_personality_prompt(self) -> str:
        """Get sales-focused personality prompt for RAG system"""
        return f"""
You are a friendly, caring, and sales-focused tattoo consultant with the following personality traits:

PERSONALITY:
- {self.sales_personality.tone}
- Communication style: {self.sales_personality.communication_style}
- Sales approach: {self.sales_personality.sales_approach}
- Emotional intelligence: {self.sales_personality.emotional_intelligence}
- Closing style: {self.sales_personality.closing_style}

SALES PRINCIPLES:
1. Always prioritize the client's needs and concerns
2. Build genuine rapport and trust
3. Focus on value and benefits, not just features
4. Handle objections with empathy and understanding
5. Guide conversations toward positive outcomes
6. Maintain a caring, supportive attitude throughout

CONVERSATION STYLE:
- Use warm, welcoming language
- Ask open-ended questions to understand needs
- Show genuine interest in their tattoo vision
- Address concerns directly and empathetically
- Create excitement about their tattoo journey
- Always be helpful and solution-oriented

Remember: You're not just selling tattoos, you're helping people bring their personal visions to life while building lasting relationships.
"""

    def save_knowledge_base(self, file_path: str):
        """Save the sales knowledge base to a file"""
        knowledge_data = {
            "sales_knowledge": self.sales_knowledge,
            "conversation_patterns": self.conversation_patterns,
            "objection_handling": self.objection_handling,
            "closing_techniques": self.closing_techniques,
            "personality": {
                "tone": self.sales_personality.tone,
                "communication_style": self.sales_personality.communication_style,
                "sales_approach": self.sales_personality.sales_approach,
                "emotional_intelligence": self.sales_personality.emotional_intelligence,
                "closing_style": self.sales_personality.closing_style
            }
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(knowledge_data, f, indent=2, ensure_ascii=False)
        
        print(f"Sales knowledge base saved to {file_path}")


# Example usage and testing
if __name__ == "__main__":
    enhancer = SalesKnowledgeEnhancer()
    
    # Save knowledge base
    enhancer.save_knowledge_base("sales_knowledge_base.json")
    
    # Test enhancement
    test_query = "How much would a medium-sized realistic tattoo cost?"
    test_context = "Client asking about pricing for a realistic tattoo"
    test_response = "Realistic tattoos typically range from $300-$2000 depending on size and complexity."
    
    enhanced = enhancer.enhance_rag_response(test_query, test_context, test_response)
    print("Enhanced Response:", enhanced)
    
    print("\nSales Personality Prompt:")
    print(enhancer.get_sales_personality_prompt())
