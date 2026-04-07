CREATE TABLE users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    phone_number        VARCHAR(20) UNIQUE NOT NULL,
    email               VARCHAR(255) UNIQUE NULL,

    hashed_password     VARCHAR(255) NOT NULL,

    is_active           BOOLEAN DEFAULT true NOT NULL,
    is_phone_verified   BOOLEAN DEFAULT false NOT NULL,

    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_profiles (
    user_id             UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,

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

CREATE INDEX idx_users_phone_number ON users(phone_number);
CREATE INDEX idx_users_email ON users(email) WHERE email IS NOT NULL;

CREATE INDEX idx_ratings_empathy ON user_ratings(empathy_score DESC);
CREATE INDEX idx_ratings_reliability ON user_ratings(reliability_score DESC);