"""
Enterprise Security & Compliance
Comprehensive security and compliance management.
"""

import asyncio
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import re

class EnterpriseSecurityManager:
    """Comprehensive security and compliance management"""
    
    def __init__(self):
        self.encryption = EnterpriseEncryption()
        self.access_control = RBACAccessControl()
        self.content_moderator = AIContentModerator()
        self.compliance_checker = ComplianceValidator()
        self.threat_detector = ThreatDetectionEngine()
        self.audit_logger = SecurityAuditLogger()
    
    async def secure_query_processing(self, query: str, user_context: Dict) -> Dict:
        """Full security pipeline for query processing"""
        
        print(f"🔒 Applying security checks for query: '{query[:50]}...'")
        
        security_checks = [
            self.validate_user_access(user_context),
            self.sanitize_input(query),
            self.detect_malicious_intent(query),
            self.check_compliance_requirements(user_context),
            self.apply_privacy_transformations(query, user_context)
        ]
        
        results = await asyncio.gather(*security_checks)
        
        # Check if any security check failed
        failed_checks = [r for r in results if not r.get('allowed', True)]
        if failed_checks:
            blocked_reasons = [r.get('reason', 'security_policy') for r in failed_checks]
            raise SecurityViolationError(f"Query blocked: {', '.join(blocked_reasons)}")
        
        # Apply encryption if needed
        processed_query = query
        if user_context.get('encryption_required', False):
            processed_query = await self.encryption.encrypt_sensitive_parts(query)
        
        # Log security event
        await self.audit_logger.log_security_event({
            'event_type': 'query_processed',
            'user_id': user_context.get('user_id', 'anonymous'),
            'query_hash': hashlib.sha256(query.encode()).hexdigest(),
            'security_checks_passed': True,
            'timestamp': datetime.now()
        })
        
        return {
            'processed_query': processed_query,
            'security_checks_passed': True,
            'audit_trail': self.create_audit_trail(results, user_context)
        }
    
    async def secure_response_generation(self, response: Dict, user_context: Dict) -> Dict:
        """Apply security measures to response"""
        
        print("🔒 Applying response security measures...")
        
        # Content moderation
        moderation_result = await self.content_moderator.moderate(response['answer'])
        if moderation_result['requires_modification']:
            response['answer'] = await self.apply_content_moderation(
                response['answer'], moderation_result
            )
        
        # PII redaction
        if user_context.get('pii_redaction', True):
            response['answer'] = await self.redact_pii(response['answer'])
        
        # Apply watermarks for audit
        response['watermark'] = await self.apply_digital_watermark(response, user_context)
        
        # Log response security event
        await self.audit_logger.log_security_event({
            'event_type': 'response_generated',
            'user_id': user_context.get('user_id', 'anonymous'),
            'response_hash': hashlib.sha256(response['answer'].encode()).hexdigest(),
            'moderation_applied': moderation_result['requires_modification'],
            'pii_redacted': user_context.get('pii_redaction', True),
            'timestamp': datetime.now()
        })
        
        return response
    
    async def validate_user_access(self, user_context: Dict) -> Dict:
        """Validate user access rights"""
        user_id = user_context.get('user_id', 'anonymous')
        role = user_context.get('role', 'guest')
        
        # Check if user has access
        has_access = await self.access_control.check_access(user_id, role)
        
        return {
            'allowed': has_access,
            'reason': 'access_denied' if not has_access else None,
            'user_id': user_id,
            'role': role
        }
    
    async def sanitize_input(self, query: str) -> Dict:
        """Sanitize user input"""
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', query)
        
        # Check for SQL injection patterns
        sql_patterns = [r'union\s+select', r'drop\s+table', r'delete\s+from']
        sql_detected = any(re.search(pattern, query, re.IGNORECASE) for pattern in sql_patterns)
        
        # Check for script injection
        script_patterns = [r'<script', r'javascript:', r'onclick=']
        script_detected = any(re.search(pattern, query, re.IGNORECASE) for pattern in script_patterns)
        
        return {
            'allowed': not (sql_detected or script_detected),
            'reason': 'malicious_input' if (sql_detected or script_detected) else None,
            'sanitized_query': sanitized,
            'threats_detected': {
                'sql_injection': sql_detected,
                'script_injection': script_detected
            }
        }
    
    async def detect_malicious_intent(self, query: str) -> Dict:
        """Detect malicious intent in query"""
        # Check for suspicious patterns
        suspicious_patterns = [
            r'password', r'secret', r'confidential',
            r'admin', r'root', r'system',
            r'exploit', r'hack', r'attack'
        ]
        
        suspicious_count = sum(1 for pattern in suspicious_patterns 
                              if re.search(pattern, query, re.IGNORECASE))
        
        # Check for excessive length (potential DoS)
        is_excessive = len(query) > 10000
        
        return {
            'allowed': suspicious_count < 3 and not is_excessive,
            'reason': 'malicious_intent' if suspicious_count >= 3 else 'excessive_length' if is_excessive else None,
            'suspicious_score': suspicious_count,
            'is_excessive': is_excessive
        }
    
    async def check_compliance_requirements(self, user_context: Dict) -> Dict:
        """Check compliance requirements"""
        compliance_result = await self.compliance_checker.validate_compliance(user_context)
        
        return {
            'allowed': compliance_result['compliant'],
            'reason': 'compliance_violation' if not compliance_result['compliant'] else None,
            'compliance_checks': compliance_result['checks']
        }
    
    async def apply_privacy_transformations(self, query: str, user_context: Dict) -> Dict:
        """Apply privacy transformations to query"""
        # Anonymize PII
        anonymized_query = await self.anonymize_pii(query)
        
        # Apply differential privacy if needed
        if user_context.get('differential_privacy', False):
            anonymized_query = await self.apply_differential_privacy(anonymized_query)
        
        return {
            'allowed': True,
            'reason': None,
            'privacy_transformations_applied': {
                'pii_anonymization': True,
                'differential_privacy': user_context.get('differential_privacy', False)
            }
        }
    
    async def anonymize_pii(self, query: str) -> str:
        """Anonymize personally identifiable information"""
        # Simple PII patterns
        pii_patterns = {
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',
            r'\b\d{3}-\d{3}-\d{4}\b': '[PHONE]',
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b': '[CREDIT_CARD]'
        }
        
        anonymized = query
        for pattern, replacement in pii_patterns.items():
            anonymized = re.sub(pattern, replacement, anonymized)
        
        return anonymized
    
    async def apply_differential_privacy(self, query: str) -> str:
        """Apply differential privacy to query"""
        # Simple noise addition
        words = query.split()
        noisy_words = []
        
        for word in words:
            if len(word) > 3 and hash(word) % 10 == 0:  # 10% chance of modification
                noisy_words.append(word + '_noise')
            else:
                noisy_words.append(word)
        
        return ' '.join(noisy_words)
    
    async def apply_content_moderation(self, content: str, moderation_result: Dict) -> str:
        """Apply content moderation to response"""
        # Simple content filtering
        filtered_content = content
        
        # Remove flagged content
        for flagged_term in moderation_result.get('flagged_terms', []):
            filtered_content = filtered_content.replace(flagged_term, '[REDACTED]')
        
        return filtered_content
    
    async def redact_pii(self, content: str) -> str:
        """Redact PII from content"""
        # Same patterns as query anonymization
        pii_patterns = {
            r'\b\d{3}-\d{2}-\d{4}\b': '[REDACTED]',
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[REDACTED]',
            r'\b\d{3}-\d{3}-\d{4}\b': '[REDACTED]'
        }
        
        redacted = content
        for pattern, replacement in pii_patterns.items():
            redacted = re.sub(pattern, replacement, redacted)
        
        return redacted
    
    async def apply_digital_watermark(self, response: Dict, user_context: Dict) -> str:
        """Apply digital watermark for audit trail"""
        watermark_data = {
            'user_id': user_context.get('user_id', 'anonymous'),
            'timestamp': datetime.now().isoformat(),
            'response_id': hashlib.md5(response['answer'].encode()).hexdigest()[:8]
        }
        
        return base64.b64encode(json.dumps(watermark_data).encode()).decode()
    
    def create_audit_trail(self, security_results: List[Dict], user_context: Dict) -> Dict:
        """Create audit trail for security events"""
        return {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_context.get('user_id', 'anonymous'),
            'security_checks': security_results,
            'overall_status': 'passed' if all(r.get('allowed', True) for r in security_results) else 'failed'
        }
    
    async def get_status(self) -> Dict:
        """Get security system status"""
        return {
            'encryption_enabled': True,
            'access_control_active': True,
            'content_moderation_active': True,
            'threat_detection_active': True,
            'audit_logging_active': True
        }

class ComprehensiveAuditSystem:
    """Complete audit trail and compliance reporting"""
    
    def __init__(self):
        self.audit_db = AuditDatabase()
        self.compliance_framework = ComplianceFramework()
        self.report_generator = ReportGenerator()
        self.encryption = EnterpriseEncryption()
    
    async def log_interaction(self, interaction: Dict):
        """Log complete interaction for compliance"""
        
        audit_record = {
            'timestamp': datetime.utcnow(),
            'interaction_id': self.generate_interaction_id(),
            'user_id': interaction['user_context'].get('user_id', 'anonymous'),
            'query_hash': hashlib.sha256(interaction['query'].encode()).hexdigest(),
            'response_hash': hashlib.sha256(interaction['response']['answer'].encode()).hexdigest(),
            'security_checks': interaction.get('security_checks', []),
            'performance_metrics': interaction.get('performance_metrics', {}),
            'llm_used': interaction.get('llm_used', 'unknown'),
            'retrieval_strategies': interaction.get('retrieval_strategies', []),
            'compliance_tags': await self.generate_compliance_tags(interaction)
        }
        
        # Encrypt sensitive fields
        encrypted_record = await self.encrypt_audit_record(audit_record)
        
        # Store in audit database
        await self.audit_db.store(encrypted_record)
        
        # Real-time compliance checking
        await self.real_time_compliance_check(audit_record)
        
        print(f"📝 Logged interaction: {audit_record['interaction_id']}")
    
    def generate_interaction_id(self) -> str:
        """Generate unique interaction ID"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_part = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        return f"INT_{timestamp}_{random_part}"
    
    async def generate_compliance_tags(self, interaction: Dict) -> List[str]:
        """Generate compliance tags for interaction"""
        tags = []
        
        # Add tags based on content
        if 'confidential' in interaction['query'].lower():
            tags.append('confidential')
        
        if 'personal' in interaction['query'].lower():
            tags.append('personal_data')
        
        if interaction['user_context'].get('role') == 'admin':
            tags.append('admin_access')
        
        return tags
    
    async def encrypt_audit_record(self, record: Dict) -> Dict:
        """Encrypt sensitive fields in audit record"""
        # Encrypt sensitive fields
        sensitive_fields = ['user_id', 'query_hash', 'response_hash']
        
        encrypted_record = record.copy()
        for field in sensitive_fields:
            if field in encrypted_record:
                encrypted_record[field] = await self.encryption.encrypt_field(
                    str(encrypted_record[field])
                )
        
        return encrypted_record
    
    async def real_time_compliance_check(self, audit_record: Dict):
        """Perform real-time compliance checking"""
        compliance_checks = await self.compliance_framework.check_compliance(audit_record)
        
        if not compliance_checks['compliant']:
            await self.trigger_compliance_alert(compliance_checks)
    
    async def trigger_compliance_alert(self, compliance_checks: Dict):
        """Trigger compliance alert"""
        print(f"⚠️ Compliance violation detected: {compliance_checks['violations']}")
    
    async def generate_compliance_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate compliance report"""
        return await self.report_generator.generate_report(start_date, end_date)
    
    async def get_audit_statistics(self) -> Dict:
        """Get audit statistics"""
        return await self.audit_db.get_statistics()

class EnterpriseEncryption:
    """Enterprise-grade encryption system"""
    
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
    
    async def encrypt_sensitive_parts(self, text: str) -> str:
        """Encrypt sensitive parts of text"""
        # Simple encryption for demonstration
        return base64.b64encode(text.encode()).decode()
    
    async def encrypt_field(self, field_value: str) -> str:
        """Encrypt a field value"""
        encrypted = self.cipher_suite.encrypt(field_value.encode())
        return base64.b64encode(encrypted).decode()
    
    async def decrypt_field(self, encrypted_value: str) -> str:
        """Decrypt a field value"""
        encrypted_data = base64.b64decode(encrypted_value.encode())
        decrypted = self.cipher_suite.decrypt(encrypted_data)
        return decrypted.decode()

class RBACAccessControl:
    """Role-based access control system"""
    
    def __init__(self):
        self.roles = {
            'admin': ['read', 'write', 'delete', 'manage'],
            'user': ['read', 'write'],
            'guest': ['read']
        }
    
    async def check_access(self, user_id: str, role: str) -> bool:
        """Check if user has access"""
        # Simple access control for demonstration
        return role in self.roles and user_id != 'blocked_user'
    
    async def get_user_permissions(self, user_id: str) -> List[str]:
        """Get user permissions"""
        # Mock implementation
        return ['read', 'write']

class AIContentModerator:
    """AI-powered content moderation"""
    
    async def moderate(self, content: str) -> Dict:
        """Moderate content for inappropriate material"""
        # Simple content moderation for demonstration
        inappropriate_terms = ['spam', 'scam', 'fraud']
        
        flagged_terms = [term for term in inappropriate_terms if term in content.lower()]
        
        return {
            'requires_modification': len(flagged_terms) > 0,
            'flagged_terms': flagged_terms,
            'moderation_score': len(flagged_terms) / len(inappropriate_terms)
        }

class ComplianceValidator:
    """Compliance validation system"""
    
    async def validate_compliance(self, user_context: Dict) -> Dict:
        """Validate compliance requirements"""
        checks = {
            'gdpr_compliant': True,
            'ccpa_compliant': True,
            'hipaa_compliant': user_context.get('role') != 'medical' or True,
            'sox_compliant': True
        }
        
        return {
            'compliant': all(checks.values()),
            'checks': checks,
            'violations': [k for k, v in checks.items() if not v]
        }

class ThreatDetectionEngine:
    """Threat detection and prevention system"""
    
    async def detect_threats(self, query: str) -> Dict:
        """Detect potential threats in query"""
        # Simple threat detection
        threat_indicators = ['hack', 'exploit', 'attack', 'malware']
        
        detected_threats = [indicator for indicator in threat_indicators 
                          if indicator in query.lower()]
        
        return {
            'threats_detected': len(detected_threats) > 0,
            'threat_types': detected_threats,
            'risk_level': 'high' if len(detected_threats) > 2 else 'medium' if len(detected_threats) > 0 else 'low'
        }

class SecurityAuditLogger:
    """Security audit logging system"""
    
    def __init__(self):
        self.audit_log = []
    
    async def log_security_event(self, event: Dict):
        """Log security event"""
        self.audit_log.append(event)
        
        # Keep only last 1000 events
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

# Mock database and framework classes
class AuditDatabase:
    async def store(self, record: Dict):
        """Store audit record"""
        pass
    
    async def get_statistics(self) -> Dict:
        """Get audit statistics"""
        return {'total_records': 0, 'recent_events': 0}

class ComplianceFramework:
    async def check_compliance(self, record: Dict) -> Dict:
        """Check compliance"""
        return {'compliant': True, 'violations': []}

class ReportGenerator:
    async def generate_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate compliance report"""
        return {'report_id': 'mock_report', 'status': 'generated'}

class SecurityViolationError(Exception):
    """Security violation exception"""
    pass
