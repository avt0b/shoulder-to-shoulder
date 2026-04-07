CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(100),
    age INTEGER CHECK (age >= 18),
    fitness_level VARCHAR(20) DEFAULT 'beginner', -- beginner, intermediate, advanced
    preferences JSONB, -- {"quiet_mode": true, "only_newbies": false, ...}
    avatar_url TEXT,
    bio TEXT
);

CREATE TABLE ratings (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    empathy_score INTEGER DEFAULT 0,           -- количество положительных действий
    reliability_score DECIMAL(5,2) DEFAULT 100.00, -- процент (0.00 - 100.00)
    total_events INTEGER DEFAULT 0,
    completed_events INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    badge_type VARCHAR(50) NOT NULL,  -- 'first_trainer', 'reliable_partner' и т.д.
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, badge_type)
);

-- Индексы
CREATE INDEX idx_ratings_empathy ON ratings(empathy_score DESC);
CREATE INDEX idx_ratings_reliability ON ratings(reliability_score DESC);