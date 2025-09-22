// APOLLO-GUIDED Advanced Security System
import { NextRequest, NextResponse } from 'next/server';
import jwt from 'jsonwebtoken';
import crypto from 'crypto';

const JWT_SECRET = process.env.JWT_SECRET || 'nexteleven-crowley-edition-2024-apollo-powered';

// Rate limiting store
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

// Rate limiting function
export function checkRateLimit(ip: string, maxRequests: number = 100, windowMs: number = 15 * 60 * 1000): boolean {
  const now = Date.now();
  const key = `rate_limit_${ip}`;
  const record = rateLimitStore.get(key);

  if (!record || now > record.resetTime) {
    rateLimitStore.set(key, { count: 1, resetTime: now + windowMs });
    return true;
  }

  if (record.count >= maxRequests) {
    return false;
  }

  record.count++;
  return true;
}

// Security headers for Next.js
export function getSecurityHeaders() {
  return {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.stripe.com http://localhost:8000; frame-src 'self' https://js.stripe.com;"
  };
}

// JWT verification middleware
export function verifyApolloToken(request: NextRequest) {
  const token = request.headers.get('authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return { valid: false, error: 'No token provided' };
  }

  try {
    const decoded = jwt.verify(token, JWT_SECRET) as any;
    return { valid: true, userId: decoded.userId, role: decoded.role };
  } catch (error) {
    return { valid: false, error: 'Invalid token' };
  }
}

// Input sanitization
export function sanitizeInput(input: string): string {
  return input
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
    .replace(/<[^>]*>/g, '') // Remove HTML tags
    .replace(/javascript:/gi, '') // Remove javascript: protocols
    .replace(/on\w+\s*=/gi, '') // Remove event handlers
    .trim()
    .substring(0, 1000); // Limit length
}

// SQL injection prevention
export function sanitizeSQL(input: string): string {
  const dangerousPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)/gi,
    /(\b(OR|AND)\s+\d+\s*=\s*\d+)/gi,
    /(\b(OR|AND)\s+['"]\s*=\s*['"])/gi,
    /(\b(OR|AND)\s+['"]\s*LIKE\s*['"])/gi,
    /(\b(OR|AND)\s+['"]\s*IN\s*\()/gi,
    /(\b(OR|AND)\s+['"]\s*BETWEEN\s+)/gi,
    /(\b(OR|AND)\s+['"]\s*EXISTS\s*\()/gi,
    /(\b(OR|AND)\s+['"]\s*NOT\s+EXISTS\s*\()/gi,
    /(\b(OR|AND)\s+['"]\s*NOT\s+IN\s*\()/gi,
  ];

  let sanitized = input;
  dangerousPatterns.forEach(pattern => {
    sanitized = sanitized.replace(pattern, '');
  });

  return sanitized;
}

// XSS protection
export function preventXSS(input: string): string {
  const xssPatterns = [
    /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
    /<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi,
    /<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi,
    /<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi,
    /<link\b[^<]*(?:(?!<\/link>)<[^<]*)*<\/link>/gi,
    /<meta\b[^<]*(?:(?!<\/meta>)<[^<]*)*<\/meta>/gi,
    /<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi,
    /javascript:/gi,
    /vbscript:/gi,
    /onload\s*=/gi,
    /onerror\s*=/gi,
    /onclick\s*=/gi,
    /onmouseover\s*=/gi,
    /onfocus\s*=/gi,
    /onblur\s*=/gi,
    /onchange\s*=/gi,
    /onsubmit\s*=/gi,
    /onreset\s*=/gi,
    /onselect\s*=/gi,
    /onkeydown\s*=/gi,
    /onkeyup\s*=/gi,
    /onkeypress\s*=/gi,
  ];

  let cleaned = input;
  xssPatterns.forEach(pattern => {
    cleaned = cleaned.replace(pattern, '');
  });

  return cleaned;
}

// CSRF protection
export function generateCSRFToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

export function verifyCSRFToken(token: string, sessionToken: string): boolean {
  return crypto.timingSafeEqual(
    Buffer.from(token, 'hex'),
    Buffer.from(sessionToken, 'hex')
  );
}

// Password strength validation
export function validatePasswordStrength(password: string): {
  valid: boolean;
  score: number;
  feedback: string[];
} {
  const feedback: string[] = [];
  let score = 0;

  if (password.length < 8) {
    feedback.push('Password must be at least 8 characters long');
  } else {
    score += 1;
  }

  if (!/[a-z]/.test(password)) {
    feedback.push('Password must contain at least one lowercase letter');
  } else {
    score += 1;
  }

  if (!/[A-Z]/.test(password)) {
    feedback.push('Password must contain at least one uppercase letter');
  } else {
    score += 1;
  }

  if (!/\d/.test(password)) {
    feedback.push('Password must contain at least one number');
  } else {
    score += 1;
  }

  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    feedback.push('Password must contain at least one special character');
  } else {
    score += 1;
  }

  if (password.length >= 12) {
    score += 1;
  }

  return {
    valid: score >= 4,
    score,
    feedback
  };
}

// IP whitelist/blacklist
const blockedIPs = new Set<string>();
const whitelistedIPs = new Set<string>();

export function isIPBlocked(ip: string): boolean {
  return blockedIPs.has(ip);
}

export function isIPWhitelisted(ip: string): boolean {
  return whitelistedIPs.has(ip);
}

export function blockIP(ip: string): void {
  blockedIPs.add(ip);
}

export function whitelistIP(ip: string): void {
  whitelistedIPs.add(ip);
}

// Request logging for security monitoring
export function logSecurityEvent(event: string, details: any, request: NextRequest) {
  const logEntry = {
    timestamp: new Date().toISOString(),
    event,
    details,
    ip: request.ip || request.headers.get('x-forwarded-for') || 'unknown',
    userAgent: request.headers.get('user-agent') || 'unknown',
    url: request.url
  };

  console.log(`🔒 APOLLO Security Event: ${JSON.stringify(logEntry)}`);
  
  // In production, send to security monitoring service
  if (process.env.NODE_ENV === 'production') {
    // Send to APOLLO security monitoring
    // This would integrate with your security monitoring system
  }
}

// Advanced authentication middleware
export function apolloAuthMiddleware(requiredRole?: string) {
  return (request: NextRequest) => {
    const auth = verifyApolloToken(request);
    
    if (!auth.valid) {
      logSecurityEvent('AUTH_FAILED', { error: auth.error }, request);
      return NextResponse.json(
        { error: 'Authentication required' },
        { status: 401 }
      );
    }

    if (requiredRole && auth.role !== requiredRole) {
      logSecurityEvent('AUTH_INSUFFICIENT_ROLE', { 
        required: requiredRole, 
        actual: auth.role 
      }, request);
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    return { userId: auth.userId, role: auth.role };
  };
}

// Security monitoring dashboard data
export function getSecurityStats() {
  return {
    blockedIPs: blockedIPs.size,
    whitelistedIPs: whitelistedIPs.size,
    memoryUsage: process.memoryUsage().heapUsed,
    uptime: process.uptime()
  };
}
