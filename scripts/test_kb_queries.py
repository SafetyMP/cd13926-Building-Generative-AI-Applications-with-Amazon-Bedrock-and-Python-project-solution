#!/usr/bin/env python3
"""
Test Bedrock Knowledge Base with various queries and configurations
"""
import boto3
import json
from typing import List, Dict, Any

# Initialize clients
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name='us-east-1')
bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')

def list_knowledge_bases() -> List[Dict]:
    """List all available knowledge bases"""
    try:
        response = bedrock_agent.list_knowledge_bases()
        return response.get('knowledgeBaseSummaries', [])
    except Exception as e:
        print(f"Error listing knowledge bases: {str(e)}")
        return []

def get_knowledge_base_details(knowledge_base_id: str) -> Dict:
    """Get details about a specific knowledge base"""
    try:
        response = bedrock_agent.get_knowledge_base(knowledgeBaseId=knowledge_base_id)
        return response.get('knowledgeBase', {})
    except Exception as e:
        print(f"Error getting knowledge base details: {str(e)}")
        return {}

def test_retrieve(knowledge_base_id: str, query: str, max_results: int = 5) -> Dict:
    """Test the retrieve API with the given query"""
    print(f"\n=== Testing RETRIEVE API ===")
    print(f"Query: {query}")
    
    try:
        response = bedrock_agent_runtime.retrieve(
            knowledgeBaseId=knowledge_base_id,
            retrievalQuery={
                'text': query
            },
            retrievalConfiguration={
                'vectorSearchConfiguration': {
                    'numberOfResults': max_results,
                    'overrideSearchType': 'HYBRID'  # Try both semantic and keyword search
                }
            }
        )
        return response
    except Exception as e:
        print(f"Error in retrieve API: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        return {}

def test_retrieve_and_generate(knowledge_base_id: str, query: str, max_results: int = 5) -> Dict:
    """Test the retrieve_and_generate API with the given query"""
    print(f"\n=== Testing RETRIEVE_AND_GENERATE API ===")
    print(f"Query: {query}")
    
    try:
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={'text': query},
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': max_results,
                            'overrideSearchType': 'HYBRID'  # Try both semantic and keyword search
                        }
                    }
                }
            }
        )
        return response
    except Exception as e:
        print(f"Error in retrieve_and_generate API: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        return {}

def test_queries(knowledge_base_id: str):
    """Test various queries against the knowledge base"""
    queries = [
        "What are the specifications of the DT1000 dump truck?",
        "Tell me about the MC750 mobile crane",
        "What is the payload capacity of the DT1000?",
        "How much can the MC750 crane lift?",
        "What are the key features of the BD850 bulldozer?",
        "What is the engine power of the FL250 forklift?",
        "What are the dimensions of the X950 excavator?"
    ]
    
    for query in queries:
        # Test with retrieve API
        response = test_retrieve(knowledge_base_id, query)
        print("\nRetrieve API Response:")
        print(json.dumps(response, indent=2, default=str))
        
        # Test with retrieve_and_generate API
        response = test_retrieve_and_generate(knowledge_base_id, query)
        print("\nRetrieve and Generate API Response:")
        print(json.dumps(response, indent=2, default=str))

if __name__ == "__main__":
    # List available knowledge bases
    print("=== Available Knowledge Bases ===")
    kbs = list_knowledge_bases()
    
    if not kbs:
        print("No knowledge bases found.")
        exit(1)
    
    for i, kb in enumerate(kbs, 1):
        print(f"{i}. ID: {kb['knowledgeBaseId']}, Name: {kb.get('name', 'N/A')}, Status: {kb.get('status', 'N/A')}")
    
    # Use the first knowledge base by default
    kb_id = kbs[0]['knowledgeBaseId']
    
    # Print knowledge base details
    print("\n=== Knowledge Base Details ===")
    kb_details = get_knowledge_base_details(kb_id)
    print(json.dumps(kb_details, indent=2, default=str))
    
    # Test queries
    print("\n=== Testing Queries ===")
    test_queries(kb_id)
