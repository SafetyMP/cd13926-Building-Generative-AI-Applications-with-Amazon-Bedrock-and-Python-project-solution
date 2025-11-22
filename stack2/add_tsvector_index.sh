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

# Add the exact tsvector index that Bedrock is asking for
echo "Adding tsvector index on chunks column..."

# First, drop the existing GIN index if it exists
execute_sql "DROP INDEX IF EXISTS bedrock_kb_chunks_idx"

# Create the tsvector index that Bedrock requires
execute_sql "
CREATE INDEX ON bedrock_integration.bedrock_kb 
USING gin (to_tsvector('english', chunks))"

echo "tsvector index on chunks column added successfully."
