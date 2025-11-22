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

# Drop the existing IVFFLAT index
echo "Dropping existing IVFFLAT index..."
execute_sql "DROP INDEX IF EXISTS bedrock_kb_embedding_idx"

# Create the HNSW index that Bedrock requires
echo "Creating HNSW index on embedding column..."

execute_sql "
CREATE INDEX ON bedrock_integration.bedrock_kb 
USING hnsw (embedding vector_cosine_ops);"

echo "HNSW index on embedding column created successfully."
