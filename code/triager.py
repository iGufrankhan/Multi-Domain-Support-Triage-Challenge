import re
from typing import Dict, Tuple, List
from config import HIGH_RISK_KEYWORDS, CRITICAL_RISK_KEYWORDS, SENSITIVE_AREAS, DOMAINS, DOMAIN_CONFIDENCE_THRESHOLDS

class TicketTriager:
    def __init__(self, corpus_loader):
        self.corpus = corpus_loader
        self.logs = []
    
    def triage(self, ticket_id: str, issue_text: str, domain: str = None) -> Dict:
        result = {
            'ticket_id': ticket_id,
            'original_issue': issue_text,
            'domain': domain or self._detect_domain(issue_text),
            'request_type': self._identify_request_type(issue_text),
            'product_area': self._classify_product_area(issue_text),
            'risk_level': self._assess_risk_level(issue_text),
            'should_escalate': False,
            'escalation_reason': None,
            'confidence': 0.0,
            'relevant_docs': [],
            'response': None,
            'decision_rationale': []
        }
        
        if result['request_type'] == 'Invalid':
            result['should_escalate'] = False
            result['response'] = "I am sorry, this is out of scope from my capabilities."
            result['justification'] = "Request is not related to supported services"
            return result
        
        result['should_escalate'], reasons = self._should_escalate_ticket(issue_text, result)
        result['decision_rationale'] = reasons
        
        if result['should_escalate']:
            result['escalation_reason'] = self._determine_escalation_reason(issue_text, result)
            result['response'] = self._generate_escalation_response(result)
        else:
            if result['domain'] == 'unknown':
                best_domain = self._find_best_domain(issue_text)
                result['domain'] = best_domain
            
            result['relevant_docs'] = self.corpus.search(
                result['domain'], 
                issue_text, 
                top_k=3
            )
            
            result['confidence'] = self._calculate_confidence(issue_text, result['relevant_docs'])
            
            threshold = DOMAIN_CONFIDENCE_THRESHOLDS.get(result['domain'], 0.50)
            
            if result['relevant_docs'] and result['confidence'] >= threshold:
                result['response'] = self._generate_response(result)
            else:
                result['should_escalate'] = True
                result['escalation_reason'] = 'Insufficient documentation available'
                result['response'] = self._generate_escalation_response(result)
        
        return result
    
    def _detect_domain(self, issue_text: str) -> str:
        text_lower = issue_text.lower()
        
        hackerrank_keywords = ['hackerrank', 'contest', 'coding challenge', 'assessment', 
                                'test', 'submission', 'problem', 'solution', 'interview prep']
        
        claude_keywords = ['claude', 'api', 'chat', 'model', 'bedrock', 'llm']
        
        visa_keywords = ['visa', 'card', 'payment', 'transaction', 'cardholder', 'merchant',
                        'traveler\'s cheques', 'balance']
        
        scores = {
            'hackerrank': sum(1 for kw in hackerrank_keywords if kw in text_lower),
            'claude': sum(1 for kw in claude_keywords if kw in text_lower),
            'visa': sum(1 for kw in visa_keywords if kw in text_lower)
        }
        
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return 'unknown'
    
    def _identify_request_type(self, issue_text: str) -> str:
        text_lower = issue_text.lower()
        
        request_patterns = {
            'Technical Issue': {
                'keywords': ['error', 'bug', 'broken', 'crash', 'fail', 'not working', 
                            'issue', 'problem', 'down', 'offline', 'timeout', 'freeze'],
                'weight': 1
            },
            'Account/Access': {
                'keywords': ['login', 'password', 'access', 'account', 'sign up', 'register',
                            'locked', 'suspended', 'disabled', 'verified', 'permission'],
                'weight': 1
            },
            'Billing': {
                'keywords': ['billing', 'charge', 'payment', 'price', 'subscription', 'cost',
                            'invoice', 'refund', 'money', 'pay'],
                'weight': 1
            },
            'Feature Request': {
                'keywords': ['feature', 'request', 'add', 'enhancement', 'wish', 'support for',
                            'would like', 'suggest'],
                'weight': 0.8
            },
            'How-To/Usage': {
                'keywords': ['how to', 'how do i', 'how can i', 'use', 'tutorial', 'help',
                            'guide', 'step', 'setup', 'configure'],
                'weight': 1
            },
            'Assessment': {
                'keywords': ['assessment', 'exam', 'test', 'score', 'result', 'submission',
                            'interview', 'challenge'],
                'weight': 1
            },
            'Security': {
                'keywords': ['fraud', 'suspicious', 'compromise', 'hack', 'breach', 'unauthorized',
                            'stolen', 'security', 'vulnerability'],
                'weight': 1.5
            }
        }
        
        max_score = 0
        best_type = 'General Inquiry'
        
        for req_type, pattern in request_patterns.items():
            score = sum(pattern['weight'] for kw in pattern['keywords'] if kw in text_lower)
            if score > max_score:
                max_score = score
                best_type = req_type
        
        if max_score == 0:
            return 'Invalid'
        
        return best_type
    
    def _classify_product_area(self, issue_text: str) -> str:
        text_lower = issue_text.lower()
        
        classifications = {
            'Account & Access': {
                'keywords': ['account', 'login', 'password', 'sign up', 'register', 'access', 
                            'locked', 'suspended', 'profile', 'user'],
                'score': 0
            },
            'Billing & Payment': {
                'keywords': ['billing', 'charge', 'payment', 'price', 'subscription', 'refund',
                            'invoice', 'money', 'cost', 'paid'],
                'score': 0
            },
            'Technical Issues': {
                'keywords': ['error', 'bug', 'crash', 'not working', 'fail', 'issue', 'problem',
                            'down', 'offline', 'timeout'],
                'score': 0
            },
            'Features & Usage': {
                'keywords': ['feature', 'how to', 'use', 'tutorial', 'guide', 'help', 'setup'],
                'score': 0
            },
            'Contests & Assessments': {
                'keywords': ['contest', 'assessment', 'exam', 'test', 'submission', 'challenge',
                            'interview', 'interview prep'],
                'score': 0
            },
            'Security & Fraud': {
                'keywords': ['fraud', 'suspicious', 'hack', 'breach', 'unauthorized', 'security',
                            'stolen', 'compromise', 'vulnerability'],
                'score': 0
            },
            'Policy & Compliance': {
                'keywords': ['policy', 'compliance', 'terms', 'gdpr', 'pii', 'legal', 'data use',
                            'terms of service'],
                'score': 0
            }
        }
        
        for area, data in classifications.items():
            data['score'] = sum(1 for kw in data['keywords'] if kw in text_lower)
        
        best_area = max(classifications.items(), key=lambda x: x[1]['score'])[0]
        return best_area if classifications[best_area]['score'] > 0 else 'Other'
    
    def _assess_risk_level(self, issue_text: str) -> str:
        text_lower = issue_text.lower()
        
        critical_count = sum(1 for keyword in CRITICAL_RISK_KEYWORDS if keyword in text_lower)
        if critical_count >= 1:
            return 'Critical'
        
        high_risk_count = sum(1 for keyword in HIGH_RISK_KEYWORDS if keyword in text_lower)
        
        if high_risk_count >= 3:
            return 'Critical'
        elif high_risk_count >= 1:
            return 'High'
        else:
            return 'Low'
    
    def _should_escalate_ticket(self, issue_text: str, result: Dict) -> Tuple[bool, List[str]]:
        text_lower = issue_text.lower()
        reasons = []
        
        if result['risk_level'] in ['Critical', 'High']:
            reasons.append(f"Risk Level: {result['risk_level']}")
            return True, reasons
        
        if result['product_area'] in SENSITIVE_AREAS:
            reasons.append(f"Sensitive Area: {result['product_area']}")
            return True, reasons
        
        for keyword in CRITICAL_RISK_KEYWORDS:
            if keyword in text_lower:
                reasons.append(f"Critical Keyword: {keyword}")
                return True, reasons
        
        if 'assessment' in text_lower or 'test' in text_lower:
            concern_keywords = ['cheat', 'unfair', 'help', 'answer', 'solution', 'plagiarism']
            if any(kw in text_lower for kw in concern_keywords):
                reasons.append("Assessment integrity concern detected")
                return True, reasons
        
        if any(kw in text_lower for kw in ['illegal', 'delete my account', 'remove my data']):
            reasons.append("Policy/compliance action requested")
            return True, reasons
        
        if any(kw in text_lower for kw in ['verify my identity', 'prove i am', 'account verification']):
            reasons.append("Account verification required")
            return True, reasons
        
        return False, reasons
    
    def _determine_escalation_reason(self, issue_text: str, result: Dict) -> str:
        text_lower = issue_text.lower()
        
        if any(kw in text_lower for kw in ['fraud', 'suspicious', 'hack', 'breach', 'identity theft']):
            return 'Security breach or fraud detected'
        elif any(kw in text_lower for kw in ['billing', 'charge', 'refund', 'payment', 'money']):
            return 'Financial transaction requires review'
        elif any(kw in text_lower for kw in ['account access', 'locked', 'suspended', 'disabled']):
            return 'Account access issue - verification needed'
        elif any(kw in text_lower for kw in ['assessment', 'test', 'cheat', 'plagiarism', 'unfair']):
            return 'Assessment integrity concern'
        elif any(kw in text_lower for kw in ['legal', 'lawsuit', 'gdpr', 'compliance']):
            return 'Legal or compliance matter'
        elif result['product_area'] in SENSITIVE_AREAS:
            return f'Sensitive area: {result["product_area"]}'
        else:
            return 'Requires human specialist review'
    
    def _find_best_domain(self, issue_text: str) -> str:
        best_domain = 'unknown'
        best_score = 0.0
        
        for domain in ['hackerrank', 'claude', 'visa']:
            docs = self.corpus.search(domain, issue_text, top_k=1)
            if docs:
                score = self._calculate_confidence(issue_text, docs)
                if score > best_score:
                    best_score = score
                    best_domain = domain
        
        return best_domain
    
    def _calculate_confidence(self, issue_text: str, docs: List[Dict]) -> float:
        if not docs:
            return 0.0
        
        doc_score = min(len(docs) / 3, 1.0) * 0.3
        
        query_words = set(w.lower() for w in issue_text.split() if len(w) > 3)
        doc_text = ' '.join([d.get('content', '') + ' ' + d.get('title', '') for d in docs]).lower()
        
        if query_words:
            matching_terms = sum(1 for word in query_words if word in doc_text)
            relevance_score = (matching_terms / len(query_words)) * 0.4
        else:
            relevance_score = 0.0
        
        completeness_score = 0.3
        final_score = doc_score + relevance_score + completeness_score
        
        return min(max(final_score, 0.0), 1.0)
    
    def _generate_response(self, result: Dict) -> str:
        response = "Based on our support documentation, here's what we found:\n\n"
        
        for i, doc in enumerate(result['relevant_docs'], 1):
            title = doc.get('title', 'Support Article')
            content = doc.get('content', 'No content available')
            response += f"**Solution {i}: {title}**\n{content}\n\n"
        
        response += f"\n_Confidence Level: {result['confidence']:.0%}_\n"
        
        if result['confidence'] < 0.65:
            response += "\n⚠️ Note: Our confidence in this answer is moderate. If this doesn't fully address your issue, please reply and we'll escalate to a specialist."
        
        return response
    
    def _generate_escalation_response(self, result: Dict) -> str:
        response = "Thank you for reaching out. Your issue requires special attention from our support team.\n\n"
        response += f"**Reason for escalation:** {result['escalation_reason']}\n\n"
        response += "Your ticket has been escalated to a human specialist who will assist you shortly.\n"
        response += f"**Ticket ID:** {result['ticket_id']}\n"
        response += f"**Category:** {result['request_type']}\n"
        response += f"**Product Area:** {result['product_area']}\n"
        response += f"**Priority Level:** {result['risk_level']}\n\n"
        response += "We appreciate your patience!"
        
        return response
    
    def add_log(self, message: str):
        self.logs.append(message)
    
    def get_logs(self) -> List[str]:
        return self.logs

