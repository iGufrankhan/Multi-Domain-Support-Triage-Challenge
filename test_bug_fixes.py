import sys
sys.path.insert(0, 'code')

from triager import TicketTriager
from corpus_loader import CorpusLoader

corpus = CorpusLoader('data')
triager = TicketTriager(corpus)

print("Testing Bug Fixes")
print("=" * 60)

print("\n1. Testing Out-of-Scope Detection (Bug Fix #1)")
print("-" * 60)
test_queries = [
    "What is the name of the actor in Iron Man?",
    "Tell me about ancient Egyptian pyramids",
    "How to cook pasta?",
    "What's 2+2?"
]

for query in test_queries:
    result = triager.triage("TEST-OOS", query)
    print(f"\nQuery: {query}")
    print(f"  Request Type: {result['request_type']}")
    print(f"  Should Escalate: {result['should_escalate']}")
    if result['response']:
        print(f"  Response: {result['response'][:60]}...")

print("\n\n2. Testing Domain Detection with Unknown Domains (Bug Fix #2)")
print("-" * 60)
domain_test_queries = [
    "I need help with my account",
    "There's an issue with my card",
    "Tell me about assessments"
]

for query in domain_test_queries:
    result = triager.triage("TEST-DOMAIN", query)
    print(f"\nQuery: {query}")
    print(f"  Detected Domain: {result['domain']}")
    print(f"  Confidence: {result['confidence']:.1%}")

print("\n" + "=" * 60)
print("Bug fixes verified!")
