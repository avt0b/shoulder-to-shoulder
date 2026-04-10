CREATE TABLE media_files (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_key        VARCHAR(255) UNIQUE NOT NULL,
    owner_id        UUID NOT NULL,
    purpose         VARCHAR(20) NOT NULL,
    content_type    VARCHAR(100) NOT NULL,
    file_size       BIGINT NOT NULL,
    status          VARCHAR(20) DEFAULT 'pending' NOT NULL,
    public_url      VARCHAR(512) NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ
);

CREATE INDEX idx_media_files_owner_id ON media_files(owner_id);
CREATE INDEX idx_media_files_file_key ON media_files(file_key);
CREATE INDEX idx_media_files_status ON media_files(status);