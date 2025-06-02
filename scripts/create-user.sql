-- Create application user
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'whereuser') THEN
      CREATE USER whereuser WITH PASSWORD 'wherepass';
   END IF;
END
$$;

-- Grant connect permission to database
GRANT CONNECT ON DATABASE whereisthisplace TO whereuser;

-- Grant usage on schema
GRANT USAGE ON SCHEMA whereisthisplace TO whereuser;
