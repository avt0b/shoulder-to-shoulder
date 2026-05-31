CREATE TABLE events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id             UUID NOT NULL,
    spot_id             UUID,
    title               VARCHAR(100) NOT NULL,
    description         TEXT,
    max_participants    INTEGER DEFAULT 10 NOT NULL,
    duration_minutes    INTEGER DEFAULT 60 NOT NULL,
    status              VARCHAR(20) DEFAULT 'pending' NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL,
    photo_url           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ,
    anonymous           BOOLEAN DEFAULT false NOT NULL
);

CREATE TABLE event_participants (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id            UUID NOT NULL REFERENCES events(id) ON DELETE CASCADE,
    user_id             UUID NOT NULL,
    status              VARCHAR(20) DEFAULT 'joined' NOT NULL,
    joined_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_events_host_id ON events(host_id);
CREATE INDEX idx_events_spot_id ON events(spot_id);
CREATE INDEX idx_events_status ON events(status);
CREATE INDEX idx_events_start_time ON events(start_time);
CREATE INDEX idx_event_participants_event_id ON event_participants(event_id);
CREATE INDEX idx_event_participants_user_id ON event_participants(user_id);
CREATE INDEX idx_event_participants_status ON event_participants(status);

ALTER TABLE event_participants ADD COLUMN photo_url TEXT;
CREATE INDEX idx_event_participants_photo ON event_participants(photo_url) WHERE photo_url IS NOT NULL;

ALTER TABLE events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;
ALTER TABLE events ADD COLUMN IF NOT EXISTS anonymous BOOLEAN DEFAULT false NOT NULL;
ALTER TABLE events ALTER COLUMN spot_id DROP NOT NULL;
