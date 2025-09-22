export default function Features() {
  const features = [
    {
      icon: '💳',
      title: 'Universal Payment Gateway',
      description: 'Accept payments securely with multiple options including credit cards, digital wallets, and crypto.',
      demo: 'Try: "I want to pay for my tattoo"'
    },
    {
      icon: '📅',
      title: 'Cosmic Appointment Booking',
      description: 'Schedule appointments with our talented artists through our intuitive booking system.',
      demo: 'Try: "Book me an appointment"'
    },
    {
      icon: '📄',
      title: 'Knowledge Vault Access',
      description: 'Access aftercare guides, portfolio PDFs, and important documents instantly.',
      demo: 'Try: "Show me aftercare instructions"'
    },
    {
      icon: '📞',
      title: 'Telepathic Callback System',
      description: 'Request callbacks from our artists for personalized consultations.',
      demo: 'Try: "Schedule a callback"'
    },
    {
      icon: '💰',
      title: 'Pricing Oracle',
      description: 'Get instant pricing estimates based on size, complexity, and placement.',
      demo: 'Try: "How much for a sleeve?"'
    },
    {
      icon: '🕐',
      title: 'Business Hours Portal',
      description: 'Check our operating hours and availability for different services.',
      demo: 'Try: "When are you open?"'
    }
  ];

  return (
    <div className="features-container">
      <h2 className="features-header">Professional Features</h2>
      
      {features.map((feature, index) => (
        <div key={index} className="feature-item">
          <div className="feature-icon">
            {feature.icon}
          </div>
          <div className="feature-text">
            <h3>{feature.title}</h3>
            <p>{feature.description}</p>
            <div className="demo-hint">
              <strong>Demo:</strong> {feature.demo}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}








