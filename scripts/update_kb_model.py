#!/usr/bin/env python3
"""
Update the Bedrock Knowledge Base to use a supported model for generation
"""
import boto3
import json
import time
from typing import Dict, Any

# Initialize clients
bedrock_agent = boto3.client('bedrock-agent', region_name='us-east-1')

# Configuration
KNOWLEDGE_BASE_ID = 'HBPKZNSUMS'
NEW_MODEL_ARN = 'arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20250219-v1:0'

def get_knowledge_base_config(knowledge_base_id: str) -> Dict[str, Any]:
    """Get the current knowledge base configuration"""
    try:
        response = bedrock_agent.get_knowledge_base(knowledgeBaseId=knowledge_base_id)
        return response.get('knowledgeBase', {})
    except Exception as e:
        print(f"Error getting knowledge base: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        raise

def update_knowledge_base_model(knowledge_base_id: str, model_arn: str) -> Dict[str, Any]:
    """Update the knowledge base to use the specified model"""
    try:
        # Get current configuration
        kb_config = get_knowledge_base_config(knowledge_base_id)
        
        # Update the model ARN in the configuration
        if 'knowledgeBaseConfiguration' in kb_config:
            if 'vectorKnowledgeBaseConfiguration' in kb_config['knowledgeBaseConfiguration']:
                # This is the embedding model, we're keeping it the same
                pass
            
            # Add or update the generation configuration
            if 'generationConfiguration' not in kb_config['knowledgeBaseConfiguration']:
                kb_config['knowledgeBaseConfiguration']['generationConfiguration'] = {}
            
            kb_config['knowledgeBaseConfiguration']['generationConfiguration'].update({
                'modelArn': model_arn,
                'promptTemplate': """\n                Human: You are an AI assistant that answers questions based on the provided context.
                
                <context>
                {context}
                </context>
                
                Question: {question}
                
                Assistant:
                """
            })
        
        # Prepare the update request
        update_params = {
            'knowledgeBaseId': knowledge_base_id,
            'name': kb_config['name'],
            'roleArn': kb_config['roleArn'],
            'knowledgeBaseConfiguration': kb_config['knowledgeBaseConfiguration'],
            'storageConfiguration': kb_config['storageConfiguration']
        }
        
        # Update the knowledge base
        response = bedrock_agent.update_knowledge_base(**update_params)
        return response
        
    except Exception as e:
        print(f"Error updating knowledge base: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        raise

def wait_for_update_completion(knowledge_base_id: str, timeout_seconds: int = 300) -> bool:
    """Wait for the knowledge base update to complete"""
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        kb = get_knowledge_base_config(knowledge_base_id)
        status = kb.get('status')
        
        if status == 'ACTIVE':
            print(f"Knowledge base update completed successfully.")
            return True
        elif status in ['UPDATING', 'CREATING']:
            print(f"Knowledge base status: {status}. Waiting...")
            time.sleep(10)  # Wait 10 seconds before checking again
        else:
            print(f"Knowledge base update failed with status: {status}")
            return False
    
    print(f"Timeout waiting for knowledge base update to complete.")
    return False

def main():
    print(f"Updating knowledge base {KNOWLEDGE_BASE_ID} to use model {NEW_MODEL_ARN}")
    
    try:
        # Update the knowledge base
        print("Starting knowledge base update...")
        response = update_knowledge_base_model(KNOWLEDGE_BASE_ID, NEW_MODEL_ARN)
        print(f"Update initiated. Knowledge base status: {response.get('status')}")
        
        # Wait for the update to complete
        print("Waiting for update to complete...")
        if wait_for_update_completion(KNOWLEDGE_BASE_ID):
            print("Knowledge base successfully updated!")
        else:
            print("Knowledge base update may not have completed successfully. Please check the AWS Console.")
        
    except Exception as e:
        print(f"Failed to update knowledge base: {str(e)}")

if __name__ == "__main__":
    main()
