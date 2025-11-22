#!/usr/bin/env python3
"""
Query Amazon Bedrock Knowledge Base

This script allows you to query a Bedrock Knowledge Base and get responses
based on the knowledge base content.
"""

import boto3
import json
import argparse
from typing import Dict, Any, List

# Initialize boto3 clients
bedrock_agent_runtime = boto3.client(
    service_name='bedrock-agent-runtime',
    region_name='us-east-1'  # Update with your AWS region if different
)

def query_knowledge_base(knowledge_base_id: str, query: str, max_results: int = 5) -> Dict[str, Any]:
    """
    Query the Bedrock Knowledge Base using retrieve_and_generate API
    
    Args:
        knowledge_base_id (str): The ID of the Bedrock Knowledge Base
        query (str): The query string
        max_results (int): Maximum number of results to return (default: 5)
        
    Returns:
        Dict: The response from the knowledge base
    """
    print(f"\n=== Debug - Querying Knowledge Base ===")
    print(f"Knowledge Base ID: {knowledge_base_id}")
    print(f"Query: {query}")
    print(f"Max Results: {max_results}")
    
    try:
        # List available knowledge bases for debugging
        try:
            print("\n--- Listing available knowledge bases ---")
            kb_client = boto3.client('bedrock-agent', region_name='us-east-1')
            response = kb_client.list_knowledge_bases()
            print("Available Knowledge Bases:")
            for kb in response.get('knowledgeBaseSummaries', []):
                print(f"- ID: {kb['knowledgeBaseId']}, Name: {kb.get('name', 'N/A')}, Status: {kb.get('status', 'N/A')}")
        except Exception as e:
            print(f"Warning: Could not list knowledge bases: {str(e)}")
        
        # Get knowledge base details
        try:
            print("\n--- Getting knowledge base details ---")
            kb_details = kb_client.get_knowledge_base(knowledgeBaseId=knowledge_base_id)
            print(f"Knowledge Base Status: {kb_details.get('knowledgeBase', {}).get('status')}")
            print(f"Knowledge Base Role ARN: {kb_details.get('knowledgeBase', {}).get('roleArn')}")
            
            # List data sources
            data_sources = kb_client.list_data_sources(
                knowledgeBaseId=knowledge_base_id
            )
            print("\nData Sources:")
            for ds in data_sources.get('dataSourceSummaries', []):
                print(f"- ID: {ds['dataSourceId']}, Name: {ds.get('name')}, Status: {ds.get('status')}")
                
                # Get data source details
                ds_details = kb_client.get_data_source(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=ds['dataSourceId']
                )
                print(f"  S3 Location: {ds_details.get('dataSource', {}).get('dataSourceConfiguration', {}).get('s3Configuration', {}).get('bucketArn')}")
                
                # List ingestion jobs
                print(f"  Ingestion Jobs:")
                jobs = kb_client.list_ingestion_jobs(
                    knowledgeBaseId=knowledge_base_id,
                    dataSourceId=ds['dataSourceId']
                )
                for job in jobs.get('ingestionJobSummaries', []):
                    print(f"  - Job ID: {job['ingestionJobId']}")
                    print(f"    Status: {job['status']}")
                    print(f"    Started: {job['startedAt']}")
                    print(f"    Updated: {job['updatedAt']}")
                    stats = job.get('statistics', {})
                    print(f"    Documents Scanned: {stats.get('numberOfDocumentsScanned', 0)}")
                    print(f"    New Documents: {stats.get('numberOfNewDocumentsIndexed', 0)}")
                    print(f"    Failed Documents: {stats.get('numberOfDocumentsFailed', 0)}")
                    
        except Exception as e:
            print(f"Warning: Could not get knowledge base details: {str(e)}")
        
        # Try to query the knowledge base using retrieve_and_generate
        print("\n--- Querying knowledge base using retrieve_and_generate ---")
        response = bedrock_agent_runtime.retrieve_and_generate(
            input={
                'text': query
            },
            retrieveAndGenerateConfiguration={
                'type': 'KNOWLEDGE_BASE',
                'knowledgeBaseConfiguration': {
                    'knowledgeBaseId': knowledge_base_id,
                    'modelArn': 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-v2',
                    'retrievalConfiguration': {
                        'vectorSearchConfiguration': {
                            'numberOfResults': max_results
                        }
                    }
                }
            }
        )
        
        print("\n=== Query Response ===")
        print(json.dumps(response, indent=2, default=str))
        return response
        
    except Exception as e:
        print(f"\n=== Error Details ===")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        if hasattr(e, 'response'):
            print("\n=== AWS Error Response ===")
            print(json.dumps(e.response, indent=2, default=str))
            
        print("\n=== Troubleshooting Tips ===")
        print("1. Verify the Knowledge Base ID is correct")
        print("2. Check if the knowledge base is in ACTIVE state")
        print("3. Verify the IAM role has necessary permissions")
        print("4. Check if the knowledge base has been synced with data")
        print("5. Check CloudWatch logs for detailed error information")
        print("6. Verify the model ARN is correct and accessible in your region")
        
        # Return empty response to allow the script to continue
        return {"retrievalResults": []}

def generate_response(model_id: str, prompt: str, knowledge_base_results: List[Dict]) -> str:
    """
    Generate a response using a Bedrock foundation model
    
    Args:
        model_id (str): The model ID to use for generation
        prompt (str): The user's query
        knowledge_base_results (List[Dict]): Retrieved results from knowledge base
        
    Returns:
        str: Generated response
    """
    # Format the knowledge base results into the prompt
    context = "\n\n".join([
        f"Source {i+1}:\n{result['content']['text']}"
        for i, result in enumerate(knowledge_base_results)
    ])
    
    # Create the prompt template
    full_prompt = f"""Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

{context}

Question: {prompt}
Helpful Answer:"""
    
    try:
        # Initialize the Bedrock Runtime client
        bedrock_runtime = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Prepare the request body based on the model
        if 'claude' in model_id.lower():
            body = json.dumps({
                "prompt": f"\n\nHuman: {full_prompt}\n\nAssistant:",
                "max_tokens_to_sample": 1000,
                "temperature": 0.5,
                "top_p": 0.9,
            })
        else:
            # Default to a generic format for other models
            body = json.dumps({
                "prompt": full_prompt,
                "max_tokens": 1000,
                "temperature": 0.5,
                "top_p": 0.9,
            })
        
        # Invoke the model
        response = bedrock_runtime.invoke_model(
            modelId=model_id,
            body=body,
            contentType='application/json',
            accept='application/json'
        )
        
        # Parse the response
        response_body = json.loads(response['body'].read())
        
        # Extract the generated text based on the model
        if 'claude' in model_id.lower():
            return response_body.get('completion', 'No response generated')
        elif 'titan' in model_id.lower():
            return response_body.get('results', [{}])[0].get('outputText', 'No response generated')
        else:
            return str(response_body)
            
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        raise

def format_references(retrieval_results: List[Dict]) -> str:
    """Format the retrieval results as references"""
    if not retrieval_results:
        return "No references found."
        
    references = []
    for i, result in enumerate(retrieval_results, 1):
        metadata = result.get('metadata', {})
        content = result.get('content', {}).get('text', 'No content')
        
        reference = f"\n--- Reference {i} ---\n"
        reference += f"Source: {metadata.get('source', 'Unknown')}\n"
        reference += f"Page: {metadata.get('page_number', 'N/A')}\n"
        reference += f"Content: {content[:200]}..."  # Show first 200 chars of content
        
        references.append(reference)
    
    return "\n".join(references)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Query Amazon Bedrock Knowledge Base')
    parser.add_argument('--knowledge-base-id', type=str, default='HBPKZNSUMS',
                       help='ID of the Bedrock Knowledge Base')
    parser.add_argument('--model-id', type=str, default='anthropic.claude-v2',
                       help='Model ID to use for generation (e.g., anthropic.claude-v2, amazon.titan-text-express-v1)')
    parser.add_argument('--query', type=str, required=False,
                       help='Query to send to the knowledge base')
    parser.add_argument('--max-results', type=int, default=3,
                       help='Maximum number of results to retrieve (default: 3)')
    
    args = parser.parse_args()
    
    # If no query provided, enter interactive mode
    if not args.query:
        print("Interactive Mode (type 'exit' to quit)")
        print("-" * 40)
        while True:
            try:
                query = input("\nEnter your question: ").strip()
                if query.lower() in ['exit', 'quit']:
                    break
                    
                if not query:
                    continue
                    
                print("\nSearching knowledge base...")
                
                # Query the knowledge base
                response = query_knowledge_base(
                    knowledge_base_id=args.knowledge_base_id,
                    query=query,
                    max_results=args.max_results
                )
                
                # Extract retrieval results
                retrieval_results = response.get('retrievalResults', [])
                
                if retrieval_results:
                    # Generate a response using the model
                    print("\nGenerating response...")
                    response_text = generate_response(
                        model_id=args.model_id,
                        prompt=query,
                        knowledge_base_results=retrieval_results
                    )
                    
                    # Display the response
                    print("\n" + "=" * 80)
                    print("RESPONSE:")
                    print("-" * 80)
                    print(response_text.strip())
                    print("\n" + "=" * 80)
                    
                    # Display references
                    print("\nREFERENCES:")
                    print("-" * 80)
                    print(format_references(retrieval_results))
                    print("=" * 80 + "\n")
                else:
                    print("No results found for your query.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
    else:
        # Non-interactive mode with a single query
        try:
            print(f"Querying knowledge base: {args.query}")
            response = query_knowledge_base(
                knowledge_base_id=args.knowledge_base_id,
                query=args.query,
                max_results=args.max_results
            )
            
            retrieval_results = response.get('retrievalResults', [])
            
            if retrieval_results:
                response_text = generate_response(
                    model_id=args.model_id,
                    prompt=args.query,
                    knowledge_base_results=retrieval_results
                )
                
                print("\n" + "=" * 80)
                print("RESPONSE:")
                print("-" * 80)
                print(response_text.strip())
                print("\n" + "=" * 80)
                
                print("\nREFERENCES:")
                print("-" * 80)
                print(format_references(retrieval_results))
                print("=" * 80 + "\n")
            else:
                print("No results found for your query.")
                
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
