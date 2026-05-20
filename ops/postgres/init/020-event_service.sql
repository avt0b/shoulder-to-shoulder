CREATE TABLE events (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    host_id             UUID NOT NULL,
    spot_id             UUID NOT NULL,
    title               VARCHAR(100) NOT NULL,
    description         TEXT,
    max_participants    INTEGER DEFAULT 10 NOT NULL,
    duration_minutes    INTEGER DEFAULT 60 NOT NULL,
    status              VARCHAR(20) DEFAULT 'pending' NOT NULL,
    start_time          TIMESTAMPTZ NOT NULL,
    photo_url           TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    anonymous           BOOLEAN DEFAULT FALSE NOT NULL
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

ALTER TABLE events ADD COLUMN updated_at TIMESTAMPTZ;

INSERT INTO events (
    id,
    host_id,
    spot_id,
    title,
    description,
    max_participants,
    duration_minutes,
    status,
    start_time,
    anonymous
) VALUES
(
    '00000000-0000-4000-8000-000000000101',
    '00000000-0000-4000-8000-000000000901',
    '00000000-0000-4000-8000-000000000001',
    'Morning Run',
    '{"text":"Easy conversational run in the park.","locationShort":"Victory Park","location":"Victory Park, central entrance","type":"running","quietCompanion":false,"level":"Новичок"}',
    8,
    60,
    'pending',
    NOW() + INTERVAL '1 day',
    FALSE
),
(
    '00000000-0000-4000-8000-000000000102',
    '00000000-0000-4000-8000-000000000902',
    '00000000-0000-4000-8000-000000000001',
    'Outdoor Strength',
    '{"text":"Calm bodyweight training session.","locationShort":"Workout Zone","location":"Outdoor workout zone","type":"strength","quietCompanion":true,"level":"Средний"}',
    6,
    60,
    'pending',
    NOW() + INTERVAL '2 days',
    TRUE
),
(
    '00000000-0000-4000-8000-000000000103',
    '00000000-0000-4000-8000-000000000903',
    '00000000-0000-4000-8000-000000000001',
    'Evening Yoga',
    '{"text":"Stretching and breathing practice after work.","locationShort":"Quiet Embankment","location":"River embankment","type":"yoga","quietCompanion":false,"level":"Открыто"}',
    10,
    60,
    'pending',
    NOW() + INTERVAL '3 days',
    FALSE
)
ON CONFLICT (id) DO NOTHING;
