#!/usr/bin/env python3
"""
Query Bedrock Knowledge Base using the retrieve API and format the results
"""
import boto3
import json
import argparse
from typing import List, Dict, Any

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')

def query_knowledge_base(knowledge_base_id: str, query: str, max_results: int = 3) -> List[Dict]:
    """
    Query the knowledge base using the retrieve API
    """
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results,
                    'overrideSearchType': 'HYBRID'  # Combines semantic and keyword search
                }
            }
        )
        return response.get('retrievalResults', [])
    except Exception as e:
        print(f"Error querying knowledge base: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        return []

def format_results(results: List[Dict]) -> str:
    """
    Format the retrieval results in a user-friendly way
    """
    if not results:
        return "No results found."
    
    formatted = ["=== Search Results ==="]
    
    for i, result in enumerate(results, 1):
        content = result.get('content', {}).get('text', '')
        source = result.get('location', {}).get('s3Location', {}).get('uri', 'Unknown source')
        score = result.get('score', 0)
        
        # Truncate content for display
        preview = content[:200] + '...' if len(content) > 200 else content
        
        formatted.append(f"\nResult {i} (Relevance: {score:.2f}):")
        formatted.append(f"Source: {source}")
        formatted.append(f"Content: {preview}")
    
    return "\n".join(formatted)

def interactive_mode(knowledge_base_id: str):
    """
    Run in interactive mode to allow multiple queries
    """
    print("=== Bedrock Knowledge Base Query Tool ===")
    print(f"Knowledge Base ID: {knowledge_base_id}")
    print("Type 'exit' to quit.\n")
    
    while True:
        try:
            query = input("\nEnter your query: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not query:
                continue
                
            print("\nSearching...")
            results = query_knowledge_base(knowledge_base_id, query)
            print("\n" + format_results(results))
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Query Bedrock Knowledge Base')
    parser.add_argument('--query', type=str, help='Query string')
    parser.add_argument('--kb-id', type=str, default='HBPKZNSUMS', 
                       help='Knowledge Base ID (default: HBPKZNSUMS)')
    parser.add_argument('--max-results', type=int, default=3,
                      help='Maximum number of results to return (default: 3)')
    
    args = parser.parse_args()
    
    if args.query:
        # Single query mode
        results = query_knowledge_base(args.kb_id, args.query, args.max_results)
        print(format_results(results))
    else:
        # Interactive mode
        interactive_mode(args.kb_id)

if __name__ == "__main__":
    main()
