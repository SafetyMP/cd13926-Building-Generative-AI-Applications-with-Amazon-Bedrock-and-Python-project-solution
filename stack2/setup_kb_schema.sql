-- Create the schema if it doesn't exist
CREATE SCHEMA IF NOT EXISTS bedrock_integration;

-- Create the bedrock_kb table with vector support
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS bedrock_integration.bedrock_kb (
    id TEXT PRIMARY KEY,
    embedding vector(1536),  -- Standard vector size for Amazon Titan Embeddings
    chunks TEXT,
    metadata JSONB
);

-- Create an index on the vector column for efficient similarity search
CREATE INDEX ON bedrock_integration.bedrock_kb USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Grant necessary permissions
GRANT USAGE ON SCHEMA bedrock_integration TO dbadmin;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA bedrock_integration TO dbadmin;
