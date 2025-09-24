"""
Privacy-Preserving Federated Retrieval
Implements encryption, differential privacy, and query transformation for federated RAG.
"""

from typing import Dict, List, Optional, Any
import json
import hashlib
import numpy as np
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re

class PrivacyManager:
    """Manages privacy transformations for federated queries"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        if encryption_key:
            self.encryption_key = encryption_key.encode()
        else:
            self.encryption_key = Fernet.generate_key()
        
        self.cipher_suite = Fernet(self.encryption_key)
        self.differential_privacy = DifferentialPrivacy()
        self.query_anonymizer = QueryAnonymizer()
    
    async def transform_query_for_node(self, query: str, node, user_context: Dict) -> str:
        """Apply privacy transformations to queries based on node privacy level"""
        
        if node.privacy_level == 'public':
            return query  # No transformation needed
        
        elif node.privacy_level == 'confidential':
            # Apply query generalization
            generalized_query = await self.generalize_query(query, user_context)
            return generalized_query
        
        elif node.privacy_level == 'restricted':
            # Apply differential privacy and encryption
            noisy_query = self.differential_privacy.add_noise_to_query(query)
            encrypted_query = self.encrypt_query(noisy_query)
            return encrypted_query
        
        else:
            return query
    
    async def generalize_query(self, query: str, user_context: Dict) -> str:
        """Generalize query to protect sensitive information"""
        
        # Simple generalization rules (in practice, use ML models)
        generalization_rules = {
            r'\b\d{4}-\d{2}-\d{2}\b': '[DATE]',  # Replace dates
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',    # Replace SSNs
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',  # Replace emails
            r'\b\d{10,}\b': '[PHONE]',  # Replace phone numbers
        }
        
        generalized_query = query
        for pattern, replacement in generalization_rules.items():
            generalized_query = re.sub(pattern, replacement, generalized_query)
        
        # Apply domain-specific generalization
        domain = user_context.get('domain', 'general')
        if domain == 'medical':
            generalized_query = self.generalize_medical_query(generalized_query)
        elif domain == 'legal':
            generalized_query = self.generalize_legal_query(generalized_query)
        
        return generalized_query
    
    def generalize_medical_query(self, query: str) -> str:
        """Apply medical-specific generalization"""
        medical_generalizations = {
            'patient': 'individual',
            'diagnosis': 'medical condition',
            'treatment': 'medical intervention',
            'symptoms': 'clinical presentation'
        }
        
        for specific, general in medical_generalizations.items():
            query = query.replace(specific, general)
        
        return query
    
    def generalize_legal_query(self, query: str) -> str:
        """Apply legal-specific generalization"""
        legal_generalizations = {
            'client': 'party',
            'case': 'legal matter',
            'lawsuit': 'legal proceeding',
            'defendant': 'accused party'
        }
        
        for specific, general in legal_generalizations.items():
            query = query.replace(specific, general)
        
        return query
    
    def encrypt_query(self, query: str) -> str:
        """Encrypt query for privacy-sensitive nodes"""
        try:
            encrypted = self.cipher_suite.encrypt(query.encode())
            return base64.b64encode(encrypted).decode()
        except Exception as e:
            print(f"Encryption failed: {e}")
            return query
    
    def decrypt_results(self, encrypted_results: str) -> Dict:
        """Decrypt results from privacy-sensitive nodes"""
        try:
            encrypted_data = base64.b64decode(encrypted_results.encode())
            decrypted = self.cipher_suite.decrypt(encrypted_data)
            return json.loads(decrypted.decode())
        except Exception as e:
            print(f"Decryption failed: {e}")
            return {}
    
    def check_privacy_compatibility(self, user_privacy_requirements: str, node_privacy_level: str) -> bool:
        """Check if user privacy requirements are compatible with node privacy level"""
        
        privacy_hierarchy = {
            'public': 0,
            'confidential': 1,
            'restricted': 2
        }
        
        user_level = privacy_hierarchy.get(user_privacy_requirements, 0)
        node_level = privacy_hierarchy.get(node_privacy_level, 0)
        
        # User can access nodes at their privacy level or lower
        return user_level >= node_level

class DifferentialPrivacy:
    """Implements differential privacy for query protection"""
    
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self.epsilon = epsilon
        self.delta = delta
        self.sensitivity = 1.0  # Query sensitivity
    
    def add_noise_to_query(self, query: str) -> str:
        """Add differential privacy noise to query terms"""
        
        words = query.split()
        noisy_words = []
        
        for word in words:
            if len(word) > 3:  # Only modify longer words
                # Small probability of replacing with synonym or similar word
                if np.random.random() < 0.1:  # 10% chance
                    noisy_words.append(self.get_synonym(word))
                else:
                    noisy_words.append(word)
            else:
                noisy_words.append(word)
        
        return ' '.join(noisy_words)
    
    def get_synonym(self, word: str) -> str:
        """Get a synonym for differential privacy"""
        synonyms = {
            'company': 'organization',
            'price': 'cost',
            'benefit': 'advantage',
            'problem': 'issue',
            'customer': 'client',
            'employee': 'worker',
            'manager': 'supervisor',
            'project': 'initiative',
            'meeting': 'session',
            'report': 'document'
        }
        return synonyms.get(word.lower(), word)
    
    def add_laplace_noise(self, value: float) -> float:
        """Add Laplace noise for differential privacy"""
        scale = self.sensitivity / self.epsilon
        noise = np.random.laplace(0, scale)
        return value + noise

class QueryAnonymizer:
    """Anonymize queries to remove personally identifiable information"""
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\d{3}-\d{3}-\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'date': r'\b\d{1,2}/\d{1,2}/\d{4}\b'
        }
    
    def anonymize_query(self, query: str) -> str:
        """Remove PII from query"""
        anonymized = query
        
        for pii_type, pattern in self.pii_patterns.items():
            anonymized = re.sub(pattern, f'[{pii_type.upper()}]', anonymized)
        
        return anonymized
    
    def detect_pii(self, query: str) -> List[str]:
        """Detect PII in query"""
        detected_pii = []
        
        for pii_type, pattern in self.pii_patterns.items():
            if re.search(pattern, query):
                detected_pii.append(pii_type)
        
        return detected_pii

class PrivacyMetrics:
    """Track privacy metrics for federated queries"""
    
    def __init__(self):
        self.metrics = {
            'total_queries': 0,
            'anonymized_queries': 0,
            'encrypted_queries': 0,
            'generalized_queries': 0,
            'pii_detected': 0
        }
    
    def record_query(self, query: str, transformations: List[str]):
        """Record privacy transformations applied to query"""
        self.metrics['total_queries'] += 1
        
        if 'anonymization' in transformations:
            self.metrics['anonymized_queries'] += 1
        
        if 'encryption' in transformations:
            self.metrics['encrypted_queries'] += 1
        
        if 'generalization' in transformations:
            self.metrics['generalized_queries'] += 1
    
    def get_privacy_report(self) -> Dict:
        """Get privacy metrics report"""
        total = self.metrics['total_queries']
        if total == 0:
            return self.metrics
        
        return {
            **self.metrics,
            'anonymization_rate': self.metrics['anonymized_queries'] / total,
            'encryption_rate': self.metrics['encrypted_queries'] / total,
            'generalization_rate': self.metrics['generalized_queries'] / total
        }

class SecureCommunication:
    """Secure communication protocols for federated nodes"""
    
    def __init__(self, shared_secret: str):
        self.shared_secret = shared_secret.encode()
        self.kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'federated_rag_salt',  # In production, use random salt
            iterations=100000,
        )
        self.key = base64.urlsafe_b64encode(self.kdf.derive(self.shared_secret))
        self.cipher = Fernet(self.key)
    
    def encrypt_message(self, message: str) -> str:
        """Encrypt message for secure transmission"""
        encrypted = self.cipher.encrypt(message.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_message(self, encrypted_message: str) -> str:
        """Decrypt received message"""
        encrypted_data = base64.b64decode(encrypted_message.encode())
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode()
    
    def create_secure_payload(self, data: Dict) -> str:
        """Create secure payload for transmission"""
        message = json.dumps(data)
        return self.encrypt_message(message)
    
    def parse_secure_payload(self, encrypted_payload: str) -> Dict:
        """Parse secure payload"""
        decrypted_message = self.decrypt_message(encrypted_payload)
        return json.loads(decrypted_message)
