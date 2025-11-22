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

# Drop and recreate the table with the correct schema
echo "Updating table schema in Aurora PostgreSQL..."

# Drop the existing table
execute_sql "DROP TABLE IF EXISTS bedrock_integration.bedrock_kb"

# Recreate the table with UUID type for the id column
execute_sql "
CREATE TABLE bedrock_integration.bedrock_kb (
    id UUID PRIMARY KEY,
    embedding vector(1536),
    chunks TEXT,
    metadata JSONB
)"

# Recreate the index
execute_sql "
CREATE INDEX ON bedrock_integration.bedrock_kb 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)"

echo "Table schema update complete."
