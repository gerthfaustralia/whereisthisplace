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

-- Grant usage and create permissions on public schema (not whereisthisplace schema)
GRANT USAGE ON SCHEMA public TO whereuser;
GRANT CREATE ON SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON SCHEMA public TO whereuser;

-- Grant all privileges on the database
GRANT ALL PRIVILEGES ON DATABASE whereisthisplace TO whereuser;

-- Make whereuser a superuser (needed for creating extensions like PostGIS and pgvector)
ALTER USER whereuser WITH SUPERUSER CREATEDB CREATEROLE;

-- Set default privileges for future objects created by any user
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO whereuser;

-- Grant privileges on existing objects (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO whereuser;