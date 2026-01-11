-- Initialize Narrative OS Database
-- This script creates the database if it doesn't exist

-- Create the database
CREATE DATABASE narrative_os;

-- Connect to the database
\c narrative_os

-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create pg_trgm extension for text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Grant all privileges to narrative user
GRANT ALL PRIVILEGES ON DATABASE narrative_os TO narrative;
