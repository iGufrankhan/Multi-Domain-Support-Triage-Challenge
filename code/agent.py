#!/usr/bin/env python3

import csv
import sys
import os
from pathlib import Path

from corpus_loader import CorpusLoader
from triager import TicketTriager
from formatter import OutputFormatter

class TriageAgent:
    def __init__(self):
        print("Initializing Multi-Domain Support Triage Agent...")
        
        corpus_path = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.corpus_loader = CorpusLoader(corpus_path)
        print(f"✓ Corpus loaded from {corpus_path}")
        
        self.triager = TicketTriager(self.corpus_loader)
        print("✓ Triage engine initialized")
        
        self.results = []
    
    def process_csv(self, input_csv: str) -> bool:
        if not os.path.exists(input_csv):
            print(f"✗ Input file not found: {input_csv}")
            return False
        
        print(f"\nProcessing tickets from {input_csv}...")
        
        try:
            with open(input_csv, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                if not reader.fieldnames:
                    print("✗ CSV file is empty or invalid")
                    return False
                
                print(f"Columns found: {reader.fieldnames}")
                
                tickets = list(reader)
                print(f"Found {len(tickets)} tickets to process\n")
                
                for i, ticket in enumerate(tickets, 1):
                    ticket_id = ticket.get('ticket_id') or ticket.get('Ticket_ID') or f'T{i:03d}'
                    
                    issue_text = (ticket.get('Issue') or 
                                 ticket.get('issue') or 
                                 ticket.get('problem') or 
                                 ticket.get('Problem') or 
                                 ticket.get('description') or 
                                 '')
                    
                    domain_raw = ticket.get('Company') or ticket.get('company') or None
                    
                    if domain_raw and domain_raw.lower() != 'none':
                        domain = domain_raw.lower()
                    else:
                        domain = None
                    
                    if not issue_text or issue_text.strip() == '':
                        print(f"  [{i}/{len(tickets)}] Ticket {ticket_id}: ✗ No issue text found")
                        continue
                    
                    print(f"  [{i}/{len(tickets)}] Triaging {ticket_id}...", end=' ')
                    result = self.triager.triage(ticket_id, issue_text, domain)
                    self.results.append(result)
                    
                    if result['should_escalate']:
                        print(f"→ ESCALATE ({result['escalation_reason']})")
                    else:
                        print(f"→ RESPOND (Confidence: {result['confidence']:.0%})")
                    
                    self.triager.add_log(
                        f"Ticket {ticket_id}: {'ESCALATE' if result['should_escalate'] else 'RESPOND'} "
                        f"({result['product_area']})"
                    )
            
            return True
        
        except Exception as e:
            print(f"✗ Error processing CSV: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def process_interactive(self):
        print("\n" + "=" * 80)
        print("INTERACTIVE TRIAGE MODE")
        print("=" * 80)
        print("Enter support issues one at a time. Type 'done' to finish.\n")
        
        ticket_num = 1
        while True:
            print(f"\nTicket #{ticket_num}")
            print("-" * 40)
            
            domain = input("Domain (hackerrank/claude/visa) [auto-detect]: ").strip()
            if domain.lower() == 'done':
                break
            
            issue = input("Issue description: ").strip()
            if issue.lower() == 'done':
                break
            
            if not issue:
                print("Issue cannot be empty")
                continue
            
            ticket_id = f"INTERACTIVE_{ticket_num}"
            result = self.triager.triage(ticket_id, issue, domain if domain else None)
            self.results.append(result)
            
            print("\n" + "-" * 40)
            print("TRIAGE RESULT:")
            print(f"  Domain: {result['domain']}")
            print(f"  Request Type: {result['request_type']}")
            print(f"  Product Area: {result['product_area']}")
            print(f"  Risk Level: {result['risk_level']}")
            print(f"  Decision: {'ESCALATE' if result['should_escalate'] else 'RESPOND'}")
            print(f"  Confidence: {result['confidence']:.0%}")
            
            if result['should_escalate']:
                print(f"  Reason: {result['escalation_reason']}")
            else:
                print(f"  Docs Found: {len(result['relevant_docs'])}")
            
            print("\nRESPONSE:")
            print(result['response'])
            
            ticket_num += 1
    
    def run(self, input_csv: str = None):
        print("=" * 80)
        print("MULTI-DOMAIN SUPPORT TRIAGE AGENT")
        print("=" * 80 + "\n")
        
        if input_csv:
            if self.process_csv(input_csv):
                self._finalize()
            else:
                print("\n✗ Failed to process CSV file")
                return False
        else:
            self.process_interactive()
            if self.results:
                self._finalize()
            else:
                print("\nNo tickets processed")
                return False
        
        return True
    
    def _finalize(self):
        print("\n" + "=" * 80)
        print("GENERATING OUTPUT FILES")
        print("=" * 80 + "\n")
        
        output_dir = os.path.dirname(__file__) or '.'
        
        csv_path = os.path.join(output_dir, 'output.csv')
        OutputFormatter.to_csv(self.results, csv_path)
        
        log_path = os.path.join(output_dir, 'log.txt')
        OutputFormatter.to_log(self.results, self.triager.get_logs(), log_path)
        
        OutputFormatter.print_summary(self.results)
        
        print("✓ Triage complete!")
        print(f"✓ Results: {csv_path}")
        print(f"✓ Logs: {log_path}")


def main():
    agent = TriageAgent()
    
    input_csv = None
    if len(sys.argv) > 1:
        input_csv = sys.argv[1]
    else:
        default_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'support_tickets.csv'
        )
        if os.path.exists(default_path):
            input_csv = default_path
            print(f"Found support_tickets.csv at {input_csv}\n")
    

    success = agent.run(input_csv)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
