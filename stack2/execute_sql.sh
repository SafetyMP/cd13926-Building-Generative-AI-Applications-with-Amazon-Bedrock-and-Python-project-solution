#!/bin/bash

# Set variables
CLUSTER_ARN="arn:aws:rds:us-east-1:045344571269:cluster:my-aurora-serverless"
SECRET_ARN="arn:aws:secretsmanager:us-east-1:045344571269:secret:my-aurora-serverless-74SSRs"
DATABASE="myapp"

# Function to execute a single SQL statement
execute_sql() {
    local sql="$1"
    echo "Executing: $sql"
    aws rds-data execute-statement \
        --resource-arn "$CLUSTER_ARN" \
        --secret-arn "$SECRET_ARN" \
        --database "$DATABASE" \
        --sql "$sql" \
        --region us-east-1
    echo "----------------------------------------"
}

# Execute each SQL statement one by one
echo "Setting up schema and table in Aurora PostgreSQL..."

# Create schema
execute_sql "CREATE SCHEMA IF NOT EXISTS bedrock_integration"

# Create extension
execute_sql "CREATE EXTENSION IF NOT EXISTS vector"

# Create table
execute_sql "
CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
    id TEXT PRIMARY KEY,
    embedding vector(1536),  -- Standard vector size for Amazon Titan Embeddings
    chunks TEXT,
    metadata JSONB
)"

# Create index
execute_sql "
CREATE INDEX IF NOT EXISTS bedrock_kb_embedding_idx 
ON bedrock_integration.bedrock_kb 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"

# Grant permissions
execute_sql "GRANT USAGE ON SCHEMA bedrock_integration TO dbadmin"
execute_sql "GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bedrock_integration TO dbadmin"

echo "Schema and table setup complete."
