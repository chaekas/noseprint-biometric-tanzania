CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS animals (
    id BIGSERIAL PRIMARY KEY,
    animal_code VARCHAR(100) NOT NULL UNIQUE,
    species VARCHAR(80) NOT NULL DEFAULT 'cattle',
    breed VARCHAR(120),
    sex VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS animal_images (
    id BIGSERIAL PRIMARY KEY,
    animal_id BIGINT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    image_path TEXT NOT NULL,
    original_filename TEXT,
    sha256 CHAR(64),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS biometric_embeddings (
    id BIGSERIAL PRIMARY KEY,
    animal_id BIGINT NOT NULL REFERENCES animals(id) ON DELETE CASCADE,
    image_id BIGINT NOT NULL REFERENCES animal_images(id) ON DELETE CASCADE,
    embedding VECTOR(512) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(image_id, model_version)
);

CREATE INDEX IF NOT EXISTS idx_animals_code ON animals(animal_code);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON biometric_embeddings(model_version);
CREATE INDEX IF NOT EXISTS idx_embeddings_cosine
    ON biometric_embeddings USING hnsw (embedding vector_cosine_ops);

CREATE TABLE IF NOT EXISTS identification_logs (
    id BIGSERIAL PRIMARY KEY,
    query_image_path TEXT,
    matched_animal_id BIGINT REFERENCES animals(id) ON DELETE SET NULL,
    similarity_score DOUBLE PRECISION,
    decision VARCHAR(20) NOT NULL,
    model_version VARCHAR(120) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
