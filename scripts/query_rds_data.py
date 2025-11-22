#!/usr/bin/env python3
"""
Query Aurora PostgreSQL using the RDS Data API
"""
import boto3
import json
import sys

def query_rds_data(sql_statement, database, secret_arn, resource_arn, region='us-east-1'):
    """Execute a SQL statement using the RDS Data API"""
    try:
        client = boto3.client('rds-data', region_name=region)
        
        response = client.execute_statement(
            secretArn=secret_arn,
            resourceArn=resource_arn,
            sql=sql_statement,
            database=database,
            includeResultMetadata=True
        )
        
        # Process and format the response
        if 'records' in response:
            columns = [col['name'] for col in response['columnMetadata']]
            rows = []
            
            for record in response['records']:
                row = {}
                for i, col in enumerate(columns):
                    # Handle different data types in the response
                    if 'stringValue' in record[i]:
                        row[col] = record[i]['stringValue']
                    elif 'longValue' in record[i]:
                        row[col] = record[i]['longValue']
                    elif 'booleanValue' in record[i]:
                        row[col] = record[i]['booleanValue']
                    elif 'doubleValue' in record[i]:
                        row[col] = record[i]['doubleValue']
                    elif 'isNull' in record[i]:
                        row[col] = None
                    else:
                        row[col] = str(record[i])
                rows.append(row)
            
            return {
                'columns': columns,
                'rows': rows
            }
        return response
        
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        if hasattr(e, 'response'):
            print(f"Error details: {e.response}")
        raise

if __name__ == "__main__":
    # Configuration - replace with your values
    SECRET_ARN = "arn:aws:secretsmanager:us-east-1:045344571269:secret:my-aurora-serverless-74SSRs"
    RESOURCE_ARN = "arn:aws:rds:us-east-1:045344571269:cluster:my-aurora-serverless"
    DATABASE = "myapp"
    
    # Query to get table structure
    print("\n=== Table Structure ===")
    structure_sql = """
    SELECT column_name, data_type, character_maximum_length
    FROM information_schema.columns 
    WHERE table_schema = 'bedrock_integration' 
    AND table_name = 'bedrock_kb';
    """
    
    print("\nExecuting query: Table structure")
    structure = query_rds_data(structure_sql, DATABASE, SECRET_ARN, RESOURCE_ARN)
    print("\nTable Structure:")
    print(json.dumps(structure, indent=2, default=str))
    
    # Query to get row count
    count_sql = "SELECT COUNT(*) as row_count FROM bedrock_integration.bedrock_kb;"
    print("\nExecuting query: Row count")
    count = query_rds_data(count_sql, DATABASE, SECRET_ARN, RESOURCE_ARN)
    print("\nRow Count:")
    print(json.dumps(count, indent=2, default=str))
    
    # Query to get sample data (first 5 rows, limited columns)
    sample_sql = """
    SELECT 
        id, 
        LEFT(chunks, 100) || '...' as text_preview,
        jsonb_pretty(metadata) as metadata
    FROM bedrock_integration.bedrock_kb 
    LIMIT 5;
    """
    
    print("\nExecuting query: Sample data")
    sample_data = query_rds_data(sample_sql, DATABASE, SECRET_ARN, RESOURCE_ARN)
    print("\nSample Data (first 5 rows):")
    print(json.dumps(sample_data, indent=2, default=str))
    
    # Check the structure of the metadata column
    metadata_sql = """
    SELECT 
        jsonb_object_keys(metadata) as metadata_keys,
        COUNT(*) as count
    FROM bedrock_integration.bedrock_kb
    GROUP BY jsonb_object_keys(metadata)
    ORDER BY count DESC;
    """
    
    print("\nExecuting query: Metadata structure")
    metadata_structure = query_rds_data(metadata_sql, DATABASE, SECRET_ARN, RESOURCE_ARN)
    print("\nMetadata Structure:")
    print(json.dumps(metadata_structure, indent=2, default=str))
    
    print(f"Executing query: {SQL.strip()}")
    
    try:
        result = query_rds_data(SQL, DATABASE, SECRET_ARN, RESOURCE_ARN)
        print("\nQuery Result:")
        print(json.dumps(result, indent=2, default=str))
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
