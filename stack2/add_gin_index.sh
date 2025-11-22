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

# Add GIN index on the chunks column
echo "Adding GIN index on chunks column..."

execute_sql "CREATE EXTENSION IF NOT EXISTS pg_trgm"

execute_sql "
CREATE INDEX IF NOT EXISTS bedrock_kb_chunks_idx 
ON bedrock_integration.bedrock_kb 
USING gin (chunks gin_trgm_ops)"

echo "GIN index on chunks column added successfully."
