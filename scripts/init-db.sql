CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS photos (
    id SERIAL PRIMARY KEY,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0.0,
    vlad vector(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos (created_at DESC);
cd ~/myarchive
cat > scripts/init-db.sql << 'EOF'
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS whereisthisplace;

-- Set search path
SET search_path TO whereisthisplace, public;

-- Create photos table with vector embeddings
CREATE TABLE IF NOT EXISTS photos (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    confidence DOUBLE PRECISION DEFAULT 0.0,
    geom GEOMETRY(Point, 4326),
    vlad vector(128),  -- WPCA128 embeddings from PatchNetVLAD
    scene_label VARCHAR(255),
    image_hash VARCHAR(64),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_photos_geom ON photos USING GIST (geom);
CREATE INDEX IF NOT EXISTS idx_photos_vlad ON photos USING hnsw (vlad vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_photos_created_at ON photos (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_photos_image_hash ON photos (image_hash);

-- Create function to update geometry from lat/lon
CREATE OR REPLACE FUNCTION update_photo_geom()
RETURNS TRIGGER AS $$
BEGIN
    NEW.geom = ST_SetSRID(ST_MakePoint(NEW.lon, NEW.lat), 4326);
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-update geometry
DROP TRIGGER IF EXISTS update_photos_geom ON photos;
CREATE TRIGGER update_photos_geom
BEFORE INSERT OR UPDATE OF lat, lon ON photos
FOR EACH ROW
EXECUTE FUNCTION update_photo_geom();

-- Create rate limit tracking table
CREATE TABLE IF NOT EXISTS rate_limits (
    ip_address INET PRIMARY KEY,
    request_count INTEGER DEFAULT 0,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_request TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for rate limit cleanup
CREATE INDEX IF NOT EXISTS idx_rate_limits_window_start ON rate_limits (window_start);

-- Create uploaded images tracking table (for ephemeral storage)
CREATE TABLE IF NOT EXISTS uploaded_images (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    file_hash VARCHAR(64) NOT NULL,
    file_path VARCHAR(500),
    upload_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ttl_hours INTEGER DEFAULT 24,
    ip_address INET,
    processed BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_uploaded_images_upload_time ON uploaded_images (upload_time);
CREATE INDEX IF NOT EXISTS idx_uploaded_images_file_hash ON uploaded_images (file_hash);

-- Grant permissions (adjust as needed)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA whereisthisplace TO whereuser;
GRANT ALL PRIVILEGES ON SCHEMA whereisthisplace TO whereuser;
EOF