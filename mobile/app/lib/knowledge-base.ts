// APOLLO Knowledge Base - Comprehensive Tattoo Industry Knowledge
export const tattooKnowledgeBase = {
  // 30% Tattoo Knowledge
  tattoo: {
    styles: {
      traditional: {
        description: "Classic American traditional tattoos with bold black outlines and limited color palette",
        characteristics: ["Bold black outlines", "Limited color palette", "Simple shading", "Iconic imagery"],
        popular_designs: ["Eagles", "Roses", "Anchors", "Hearts", "Skulls", "Dragons"],
        placement: ["Arms", "Chest", "Back", "Legs"],
        pricing_range: "$150-$500",
        session_time: "2-4 hours",
        aftercare: "Standard aftercare with emphasis on keeping bold lines crisp"
      },
      realistic: {
        description: "Photorealistic tattoos that look like photographs or detailed artwork",
        characteristics: ["Photorealistic detail", "Complex shading", "Full color spectrum", "High contrast"],
        popular_designs: ["Portraits", "Animals", "Nature scenes", "Objects", "Landscapes"],
        placement: ["Arms", "Back", "Chest", "Thighs"],
        pricing_range: "$300-$2000",
        session_time: "4-8 hours",
        aftercare: "Gentle care to preserve fine details and color vibrancy"
      },
      geometric: {
        description: "Mathematical patterns, sacred geometry, and abstract geometric designs",
        characteristics: ["Precise lines", "Mathematical patterns", "Symmetrical designs", "Minimal shading"],
        popular_designs: ["Mandala", "Sacred geometry", "Abstract patterns", "Geometric animals"],
        placement: ["Arms", "Back", "Chest", "Ribs"],
        pricing_range: "$200-$800",
        session_time: "3-6 hours",
        aftercare: "Careful handling to maintain line precision"
      },
      watercolor: {
        description: "Tattoos that mimic watercolor painting with flowing colors and soft edges",
        characteristics: ["Flowing colors", "Soft edges", "No black outlines", "Painterly effect"],
        popular_designs: ["Flowers", "Abstract art", "Animals", "Landscapes"],
        placement: ["Arms", "Thighs", "Back", "Ribs"],
        pricing_range: "$250-$1000",
        session_time: "3-5 hours",
        aftercare: "Extra care to preserve color vibrancy and prevent fading"
      },
      blackwork: {
        description: "Solid black tattoos with bold, graphic designs",
        characteristics: ["Solid black ink", "Bold designs", "High contrast", "Graphic style"],
        popular_designs: ["Tribal patterns", "Abstract shapes", "Animals", "Geometric designs"],
        placement: ["Arms", "Legs", "Back", "Chest"],
        pricing_range: "$200-$600",
        session_time: "2-5 hours",
        aftercare: "Standard aftercare with focus on preventing scabbing"
      },
      dotwork: {
        description: "Tattoos created entirely with dots, creating shading and texture",
        characteristics: ["Dot-based shading", "Intricate patterns", "Textural effects", "Meditative quality"],
        popular_designs: ["Mandala", "Sacred geometry", "Animals", "Abstract patterns"],
        placement: ["Arms", "Back", "Chest", "Ribs"],
        pricing_range: "$300-$1200",
        session_time: "4-8 hours",
        aftercare: "Gentle care to prevent dot distortion"
      }
    },
    body_parts: {
      arm: {
        description: "Most popular placement for tattoos",
        pain_level: "Low to Medium",
        healing_time: "2-3 weeks",
        considerations: ["Easy to show/hide", "Good for detailed work", "Minimal movement during healing"],
        popular_styles: ["Traditional", "Realistic", "Geometric", "Sleeves"]
      },
      back: {
        description: "Large canvas for detailed work",
        pain_level: "Low to Medium",
        healing_time: "3-4 weeks",
        considerations: ["Large surface area", "Good for complex designs", "Harder to care for"],
        popular_styles: ["Realistic", "Geometric", "Large traditional pieces"]
      },
      chest: {
        description: "Bold placement for statement pieces",
        pain_level: "Medium to High",
        healing_time: "2-3 weeks",
        considerations: ["High visibility", "Sensitive area", "Good for symmetrical designs"],
        popular_styles: ["Traditional", "Realistic", "Geometric"]
      },
      leg: {
        description: "Good for larger pieces and detailed work",
        pain_level: "Low to Medium",
        healing_time: "2-3 weeks",
        considerations: ["Easy to care for", "Good for detailed work", "Can be hidden"],
        popular_styles: ["Realistic", "Traditional", "Geometric", "Sleeves"]
      },
      hand: {
        description: "High visibility, high commitment placement",
        pain_level: "High",
        healing_time: "2-3 weeks",
        considerations: ["Very visible", "Hard to hide", "May affect employment", "Requires frequent touch-ups"],
        popular_styles: ["Small traditional", "Geometric", "Minimalist"]
      },
      neck: {
        description: "Bold, highly visible placement",
        pain_level: "High",
        healing_time: "2-3 weeks",
        considerations: ["Very visible", "Hard to hide", "May affect employment", "Sensitive area"],
        popular_styles: ["Small traditional", "Script", "Minimalist"]
      }
    },
    aftercare: {
      immediate: {
        steps: [
          "Keep bandage on for 2-4 hours",
          "Wash hands before touching tattoo",
          "Gently wash with antibacterial soap",
          "Pat dry with clean towel",
          "Apply thin layer of healing ointment"
        ],
        timeline: "First 24 hours"
      },
      healing: {
        steps: [
          "Wash 2-3 times daily with antibacterial soap",
          "Apply thin layer of healing ointment 2-3 times daily",
          "Avoid direct sunlight",
          "Don't pick at scabs",
          "Wear loose, breathable clothing",
          "Avoid swimming and hot tubs"
        ],
        timeline: "2-4 weeks"
      },
      long_term: {
        steps: [
          "Apply sunscreen daily (SPF 30+)",
          "Moisturize regularly",
          "Avoid excessive sun exposure",
          "Schedule touch-ups as needed",
          "Maintain healthy skin"
        ],
        timeline: "Lifetime"
      },
      products: {
        recommended: [
          "Antibacterial soap (Dial, Cetaphil)",
          "Healing ointment (Aquaphor, A&D)",
          "Fragrance-free moisturizer",
          "Sunscreen (SPF 30+)",
          "Clean towels and bedding"
        ],
        avoid: [
          "Perfumed products",
          "Alcohol-based products",
          "Scratching or picking",
          "Tight clothing",
          "Excessive sun exposure"
        ]
      }
    },
    pricing: {
      factors: [
        "Size and complexity",
        "Body placement",
        "Artist experience",
        "Time required",
        "Color vs black and gray",
        "Touch-ups needed",
        "Shop location",
        "Design uniqueness"
      ],
      ranges: {
        small: "$50-$200",
        medium: "$200-$500",
        large: "$500-$1500",
        sleeve: "$1000-$5000",
        back_piece: "$2000-$8000"
      },
      hourly_rates: "$100-$300 per hour"
    }
  },

  // 30% Customer Service
  customer_service: {
    communication: {
      active_listening: [
        "Maintain eye contact",
        "Ask clarifying questions",
        "Paraphrase to confirm understanding",
        "Avoid interrupting",
        "Show empathy and understanding"
      ],
      phone_etiquette: [
        "Answer within 3 rings",
        "Greet warmly and professionally",
        "Identify yourself and shop",
        "Listen without interrupting",
        "Take detailed notes",
        "Confirm all details",
        "End with next steps"
      ],
      email_communication: [
        "Respond within 24 hours",
        "Use professional subject lines",
        "Be clear and concise",
        "Include all necessary information",
        "Use proper grammar and spelling",
        "Include contact information"
      ]
    },
    appointment_management: {
      booking_process: [
        "Collect contact information",
        "Determine tattoo preferences",
        "Check artist availability",
        "Explain pricing and timeline",
        "Schedule consultation if needed",
        "Send confirmation details",
        "Provide preparation instructions"
      ],
      consultation_guidelines: [
        "Review design ideas",
        "Discuss placement and size",
        "Explain process and timeline",
        "Address concerns and questions",
        "Provide accurate pricing",
        "Schedule follow-up if needed"
      ],
      day_of_appointment: [
        "Confirm appointment 24 hours prior",
        "Prepare workspace and materials",
        "Review design and placement",
        "Explain process to client",
        "Ensure comfort throughout session",
        "Provide aftercare instructions"
      ]
    },
    problem_resolution: {
      common_issues: [
        "Scheduling conflicts",
        "Pricing misunderstandings",
        "Design changes",
        "Healing problems",
        "Touch-up requests",
        "Cancellation policies"
      ],
      resolution_steps: [
        "Listen to client concerns",
        "Acknowledge the issue",
        "Apologize if appropriate",
        "Offer solutions",
        "Follow up to ensure satisfaction",
        "Document for future reference"
      ]
    },
    follow_up: {
      post_appointment: [
        "Check in after 24 hours",
        "Follow up after 1 week",
        "Schedule touch-up if needed",
        "Ask for feedback",
        "Maintain client relationship"
      ],
      long_term: [
        "Send birthday messages",
        "Share new artist work",
        "Offer special promotions",
        "Request reviews and referrals",
        "Maintain portfolio updates"
      ]
    }
  },

  // 30% Sales
  sales: {
    consultation_sales: {
      needs_assessment: [
        "What type of tattoo are you interested in?",
        "Have you had tattoos before?",
        "What's your budget range?",
        "When would you like to get it done?",
        "Do you have any concerns or questions?"
      ],
      value_proposition: [
        "Experienced, licensed artists",
        "Clean, professional environment",
        "High-quality materials and equipment",
        "Comprehensive aftercare support",
        "Portfolio of excellent work",
        "Competitive pricing"
      ],
      objection_handling: {
        price: [
          "Explain value and quality",
          "Break down pricing factors",
          "Offer payment plans",
          "Compare to other shops",
          "Emphasize long-term value"
        ],
        timing: [
          "Explain booking process",
          "Offer consultation first",
          "Discuss flexible scheduling",
          "Highlight preparation time",
          "Create urgency appropriately"
        ],
        concerns: [
          "Address pain concerns",
          "Explain healing process",
          "Show portfolio examples",
          "Provide references",
          "Offer consultation"
        ]
      }
    },
    upselling: {
      additional_services: [
        "Touch-up sessions",
        "Design modifications",
        "Additional pieces",
        "Aftercare products",
        "Gift certificates"
      ],
      techniques: [
        "Suggest complementary designs",
        "Offer package deals",
        "Highlight seasonal promotions",
        "Recommend aftercare products",
        "Suggest future appointments"
      ]
    },
    closing_techniques: [
      "Assume the sale",
      "Create urgency",
      "Offer incentives",
      "Address final concerns",
      "Confirm next steps",
      "Schedule appointment"
    ],
    retention: [
      "Excellent service delivery",
      "Follow-up communication",
      "Loyalty programs",
      "Referral incentives",
      "Social media engagement",
      "Portfolio updates"
    ]
  },

  // 10% Conversation
  conversation: {
    ice_breakers: [
      "How did you hear about our shop?",
      "What brings you in today?",
      "Have you been thinking about this tattoo for a while?",
      "What's the story behind this design?",
      "Are you excited about getting your first tattoo?"
    ],
    rapport_building: [
      "Share relevant personal experiences",
      "Ask about their interests",
      "Find common ground",
      "Show genuine interest",
      "Be authentic and friendly"
    ],
    conversation_topics: [
      "Tattoo experiences",
      "Design inspiration",
      "Art and creativity",
      "Personal interests",
      "Shop history and artists",
      "Aftercare tips",
      "Future tattoo plans"
    ],
    active_engagement: [
      "Ask open-ended questions",
      "Listen actively",
      "Share relevant stories",
      "Show enthusiasm",
      "Be present and focused"
    ]
  }
};

export default tattooKnowledgeBase;
