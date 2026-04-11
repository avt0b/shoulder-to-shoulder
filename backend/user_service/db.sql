CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    phone_number        VARCHAR(20) UNIQUE NOT NULL,
    email               VARCHAR(255) UNIQUE NULL,

    hashed_password     VARCHAR(255) NOT NULL,

    role                VARCHAR(20) DEFAULT 'user' NOT NULL,
    CONSTRAINT chk_users_role CHECK (role IN ('user', 'moderator', 'superuser')),

    is_active           BOOLEAN DEFAULT true NOT NULL,
    is_phone_verified   BOOLEAN DEFAULT false NOT NULL,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_profiles (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    city                VARCHAR(100),
    display_name        VARCHAR(100) NOT NULL,
    age                 INTEGER CHECK (age >= 18),
    fitness_level       VARCHAR(20) DEFAULT 'beginner' NOT NULL,
    bio                 TEXT,
    avatar_url          TEXT,
    preferences         JSONB DEFAULT '{}'::jsonb NOT NULL,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_ratings (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

    empathy_score       INTEGER DEFAULT 0 NOT NULL,
    reliability_score   DECIMAL(5,2) DEFAULT 100.00 NOT NULL,

    total_events        INTEGER DEFAULT 0 NOT NULL,
    completed_events    INTEGER DEFAULT 0 NOT NULL,

    last_updated        TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE badges (
    id                  SERIAL PRIMARY KEY,
    user_id             UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_type          VARCHAR(50) NOT NULL,
    awarded_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    UNIQUE(user_id, badge_type)
);

CREATE TABLE workout_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    city VARCHAR(100) NOT NULL,
    preferred_time TIMESTAMPTZ NOT NULL,
    duration_minutes INT DEFAULT 60,
    fitness_level VARCHAR(50),
    description TEXT,
    status VARCHAR(20) DEFAULT 'open',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE request_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id UUID NOT NULL REFERENCES workout_requests(id),
    responder_id UUID NOT NULL REFERENCES users(id),
    message TEXT,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_responses_request ON request_responses(request_id);

CREATE INDEX idx_match_requests_receiver ON match_requests(receiver_id, status);
CREATE INDEX idx_match_requests_city_time ON match_requests(city, preferred_time);

CREATE INDEX idx_match_requests_receiver ON match_requests(receiver_id, status);
CREATE INDEX idx_match_requests_city_time ON match_requests(city, preferred_time);

CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;
CREATE INDEX idx_users_role ON users(role);


CREATE INDEX idx_ratings_empathy ON user_ratings(empathy_score DESC);
CREATE INDEX idx_ratings_reliability ON user_ratings(reliability_score DESC);

CREATE INDEX idx_user_profiles_city ON user_profiles(city);

ALTER TABLE user_profiles ADD COLUMN theme VARCHAR(10) DEFAULT 'light' NOT NULL;

ALTER TABLE workout_requests
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ;

ALTER TABLE workout_requests
ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW();