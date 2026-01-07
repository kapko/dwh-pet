-- DWH Schemas (Medallion Architecture)

-- Bronze layer: raw data as-is from sources
CREATE SCHEMA IF NOT EXISTS bronze;

-- Silver layer: cleaned, validated data
CREATE SCHEMA IF NOT EXISTS silver;

-- Gold layer: business-ready aggregates and marts
CREATE SCHEMA IF NOT EXISTS gold;

-- Metabase database
CREATE DATABASE metabase;
