-- Create application user with superuser privileges
DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'whereuser') THEN
      CREATE USER whereuser WITH PASSWORD 'wherepass' SUPERUSER CREATEDB CREATEROLE;
   ELSE
      ALTER USER whereuser WITH PASSWORD 'wherepass' SUPERUSER CREATEDB CREATEROLE;
   END IF;
END
$$;

-- Grant connect permission to database
GRANT CONNECT ON DATABASE whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON DATABASE whereisthisplace TO whereuser;

-- Grant permissions on BOTH schemas (public and whereisthisplace)
GRANT USAGE ON SCHEMA public TO whereuser;
GRANT CREATE ON SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON SCHEMA public TO whereuser;

GRANT USAGE ON SCHEMA whereisthisplace TO whereuser;
GRANT CREATE ON SCHEMA whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON SCHEMA whereisthisplace TO whereuser;

-- Set default privileges for future objects in both schemas
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TYPES TO whereuser;

ALTER DEFAULT PRIVILEGES IN SCHEMA whereisthisplace GRANT ALL ON TABLES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA whereisthisplace GRANT ALL ON SEQUENCES TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA whereisthisplace GRANT ALL ON FUNCTIONS TO whereuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA whereisthisplace GRANT ALL ON TYPES TO whereuser;

-- Grant privileges on existing objects in both schemas
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO whereuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO whereuser;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA whereisthisplace TO whereuser;