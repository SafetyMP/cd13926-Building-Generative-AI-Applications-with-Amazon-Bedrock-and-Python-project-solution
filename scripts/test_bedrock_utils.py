#!/usr/bin/env python3
"""
Test script to demonstrate using the functions from bedrock_utils.py
"""
import sys
import json
from pathlib import Path

# Add the parent directory to the path to import bedrock_utils
sys.path.append(str(Path(__file__).parent.parent))
from bedrock_utils import query_knowledge_base, generate_response, valid_prompt

def test_query(knowledge_base_id, query):
    """Test querying the knowledge base"""
    print(f"\n{'='*80}")
    print(f"TESTING QUERY: {query}")
    print(f"{'='*80}")
    
    # Check if the prompt is valid (related to heavy machinery)
    print("\nValidating prompt...")
    is_valid = valid_prompt(query, "anthropic.claude-3-sonnet-20240229-v1:0")
    print(f"Prompt is valid (related to heavy machinery): {is_valid}")
    
    if not is_valid:
        print("This query doesn't seem to be related to heavy machinery. Please try a different query.")
        return
    
    # Query the knowledge base
    print("\nQuerying knowledge base...")
    results = query_knowledge_base(query, knowledge_base_id)
    
    if not results:
        print("No results found in the knowledge base.")
        return
    
    # Display the retrieval results
    print("\n=== RETRIEVAL RESULTS ===")
    for i, result in enumerate(results, 1):
        content = result.get('content', {}).get('text', '')
        source = result.get('location', {}).get('s3Location', {}).get('uri', 'Unknown source')
        score = result.get('score', 0)
        
        # Truncate content for display
        preview = content[:200] + '...' if len(content) > 200 else content
        
        print(f"\n=== Result {i} (Relevance: {score:.2f}) ===")
        print(f"Source: {source}")
        print(f"Content: {preview}")
    
    # Prepare context for generation
    context = "\n\n".join([r.get('content', {}).get('text', '') for r in results])
    
    # Generate a response using the retrieved context
    prompt = f"""You are a helpful assistant that provides information about heavy machinery.
    
    Here is some relevant information from the knowledge base:
    {context}
    
    Based on this information, please answer the following question:
    {query}
    
    If the information is not sufficient to answer the question, please say so.
    """
    
    print("\n=== GENERATED RESPONSE ===")
    response = generate_response(
        prompt=prompt,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        temperature=0.3,
        top_p=0.9
    )
    print(response)

def main():
    # Knowledge Base ID (replace with your actual KB ID)
    KNOWLEDGE_BASE_ID = "HBPKZNSUMS"
    
    # Test queries
    test_queries = [
        "What are the specifications of the DT1000 dump truck?",
        "What is the maximum lifting capacity of the MC750 crane?",
        "Tell me about the features of the BD850 bulldozer."
    ]
    
    # Run tests
    for query in test_queries:
        test_query(KNOWLEDGE_BASE_ID, query)
    
    # Interactive mode
    print("\n" + "="*80)
    print("INTERACTIVE MODE (type 'exit' to quit)")
    print("="*80)
    
    while True:
        try:
            query = input("\nEnter your question about heavy machinery: ").strip()
            
            if query.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not query:
                continue
                
            test_query(KNOWLEDGE_BASE_ID, query)
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
