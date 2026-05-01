import csv
from typing import List, Dict
from datetime import datetime

class OutputFormatter:
    @staticmethod
    def to_csv(results: List[Dict], output_file: str = 'output.csv'):
        if not results:
            print("No results to write")
            return
        
        fieldnames = [
            'Response',
            'Product Area',
            'Status',
            'Request Type'
        ]
        
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    status = 'Escalated' if result.get('should_escalate') else 'Replied'
                    
                    request_type = OutputFormatter._map_request_type(result.get('request_type', ''), result)
                    
                    row = {
                        'Response': result.get('response', '').replace('\n', ' '),
                        'Product Area': result.get('product_area', 'Other'),
                        'Status': status,
                        'Request Type': request_type
                    }
                    writer.writerow(row)
            
            print(f"✓ Predictions written to {output_file}")
        except Exception as e:
            print(f"✗ Error writing to CSV: {e}")
    
    @staticmethod
    def _map_request_type(original_type: str, result: Dict) -> str:
        original_lower = original_type.lower()
        
        if 'invalid' in original_lower or 'out of scope' in original_lower.lower():
            return 'invalid'
        elif 'feature' in original_lower or 'request' in original_lower:
            return 'feature_request'
        elif 'bug' in original_lower or 'technical' in original_lower or 'error' in original_lower:
            return 'bug'
        else:
            return 'product_issue'  # Default
    
    @staticmethod
    def _generate_justification(result: Dict) -> str:
        if result.get('should_escalate'):
            reason = result.get('escalation_reason', 'Escalated for human review')
            return f"Escalated: {reason}"
        else:
            confidence = result.get('confidence', 0)
            num_docs = len(result.get('relevant_docs', []))
            return f"Responded with {num_docs} relevant docs (confidence: {confidence:.0%})"
    
    @staticmethod
    def to_log(results: List[Dict], logs: List[str], log_file: str = 'log.txt'):
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write("MULTI-DOMAIN SUPPORT TRIAGE AGENT - DECISION LOG\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")
                
                if logs:
                    f.write("SYSTEM LOGS:\n")
                    f.write("-" * 80 + "\n")
                    for log in logs:
                        f.write(f"{log}\n")
                    f.write("\n")
                
                f.write("TRIAGE RESULTS DETAIL:\n")
                f.write("=" * 80 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"TICKET {i}: {result.get('ticket_id', 'Unknown')}\n")
                    f.write("-" * 80 + "\n")
                    
                    f.write(f"Original Issue:\n{result.get('original_issue', 'N/A')}\n\n")
                    
                    f.write("TRIAGE ANALYSIS:\n")
                    f.write(f"  Domain: {result.get('domain', 'N/A')}\n")
                    f.write(f"  Request Type: {result.get('request_type', 'N/A')}\n")
                    f.write(f"  Product Area: {result.get('product_area', 'N/A')}\n")
                    f.write(f"  Risk Level: {result.get('risk_level', 'N/A')}\n")
                    f.write(f"  Confidence: {result.get('confidence', 0):.2%}\n\n")
                    
                    action = "ESCALATE" if result.get('should_escalate') else "RESPOND"
                    f.write(f"DECISION: {action}\n")
                    f.write(f"Reason: {result.get('escalation_reason') or 'Sufficient documentation available'}\n\n")
                    
                    if result.get('relevant_docs'):
                        f.write("RELEVANT DOCUMENTATION RETRIEVED:\n")
                        for j, doc in enumerate(result['relevant_docs'], 1):
                            f.write(f"  {j}. {doc.get('title', 'Unknown')}\n")
                        f.write("\n")
                    
                    f.write("GENERATED RESPONSE:\n")
                    f.write(f"{result.get('response', 'No response generated')}\n")
                    f.write("\n" + "=" * 80 + "\n\n")
                
                f.write("SUMMARY STATISTICS:\n")
                f.write("-" * 80 + "\n")
                total_tickets = len(results)
                escalated = sum(1 for r in results if r.get('should_escalate'))
                responded = total_tickets - escalated
                
                f.write(f"Total Tickets: {total_tickets}\n")
                f.write(f"Escalated: {escalated} ({escalated/total_tickets*100:.1f}%)\n")
                f.write(f"Responded: {responded} ({responded/total_tickets*100:.1f}%)\n")
                
                avg_confidence = sum(r.get('confidence', 0) for r in results) / total_tickets if total_tickets > 0 else 0
                f.write(f"Average Confidence: {avg_confidence:.2%}\n")
                
                risk_counts = {}
                for result in results:
                    risk = result.get('risk_level', 'Unknown')
                    risk_counts[risk] = risk_counts.get(risk, 0) + 1
                
                f.write(f"Risk Distribution:\n")
                for risk, count in sorted(risk_counts.items()):
                    f.write(f"  {risk}: {count}\n")
            
            print(f"✓ Detailed logs written to {log_file}")
        except Exception as e:
            print(f"Error writing logs: {e}")
    
    @staticmethod
    def print_summary(results: List[Dict]):
        print("\n" + "=" * 80)
        print("TRIAGE SUMMARY")
        print("=" * 80)
        
        total = len(results)
        if total == 0:
            print("\n⚠ No tickets were processed")
            print("=" * 80 + "\n")
            return
        
        escalated = sum(1 for r in results if r.get('should_escalate'))
        responded = total - escalated
        
        print(f"\nTotal Tickets Processed: {total}")
        print(f"  ✓ Responded: {responded} ({responded/total*100:.1f}%)")
        print(f"  ⚠ Escalated: {escalated} ({escalated/total*100:.1f}%)")
        
        avg_confidence = sum(r.get('confidence', 0) for r in results) / total if total > 0 else 0
        print(f"\nAverage Confidence: {avg_confidence:.2%}")
        
        risk_counts = {}
        for result in results:
            risk = result.get('risk_level', 'Unknown')
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        print(f"\nRisk Distribution:")
        for risk in ['Critical', 'High', 'Low']:
            count = risk_counts.get(risk, 0)
            print(f"  {risk}: {count}")
        
        domain_counts = {}
        for result in results:
            domain = result.get('domain', 'Unknown')
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        print(f"\nDomain Distribution:")
        for domain, count in sorted(domain_counts.items()):
            print(f"  {domain}: {count}")
        
        print("\n" + "=" * 80 + "\n")
