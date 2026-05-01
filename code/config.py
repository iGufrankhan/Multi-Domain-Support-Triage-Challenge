DOMAINS = {
    'hackerrank': 'HackerRank Support',
    'claude': 'Claude Help Center',
    'visa': 'Visa Support'
}

CRITICAL_RISK_KEYWORDS = [
    'fraud', 'suspicious activity', 'hack', 'breach', 'compromise',
    'identity theft', 'unauthorized access', 'stolen',
    'security vulnerability', 'data leak',
    'lawsuit', 'legal action', 'regulatory', 'investigation'
]

HIGH_RISK_KEYWORDS = [
    'fraud', 'suspicious', 'hack', 'breach', 'compromise',
    'billing', 'charge', 'refund', 'payment', 'double charge',
    'account access', 'locked', 'suspended', 'disabled',
    'permissions', 'authorization', 'authentication', 'verified',
    'legal', 'lawsuit', 'compliance', 'gdpr', 'pii', 'sensitive data',
    'password', 'credential', 'secret', 'api key',
    'assessment', 'cheating', 'plagiarism', 'violation', 'unfair',
    'identity', 'personal info', 'private', 'data use'
]

SENSITIVE_AREAS = [
    'Billing & Payment',
    'Security & Fraud',
    'Policy & Compliance',
    'Account Access & Permissions',
    'Assessment Integrity'
]

PRODUCT_AREAS = {
    'Account & Access',
    'Billing & Payment',
    'Technical Issues',
    'Features & Usage',
    'Contests & Assessments',
    'Security & Fraud',
    'Policy & Compliance',
    'Other'
}

ESCALATION_RULES = {
    'contains_billing': True,
    'contains_security': True,
    'contains_account_access': True,
    'contains_assessment_concerns': True,
    'low_confidence': 0.6,
}

DOMAIN_CONFIDENCE_THRESHOLDS = {
    'hackerrank': 0.50,
    'claude': 0.55,
    'visa': 0.70
}

LOG_FILE = 'log.txt'
OUTPUT_CSV = 'output.csv'
