CREATE TABLE IF NOT EXISTS guilds (
    id BIGINT PRIMARY KEY,
    added BIGINT,
    nsfw BOOLEAN DEFAULT TRUE,
    alert_cid BIGINT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS admins (
    id BIGINT PRIMARY KEY,
    added BIGINT,
    add_others BOOLEAN,
    added_by BIGINT
);

CREATE TABLE IF NOT EXISTS slanders (
    id SERIAL,
    message TEXT PRIMARY KEY,
    creator BIGINT NOT NULL,
    nsfw BOOLEAN NOT NULL DEFAULT TRUE,
    approved BOOLEAN, -- approved: True = approved, False = denied, Null = awaiting approval
    notified BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS slander_log (
    id SERIAL PRIMARY KEY,
    message TEXT,
    gid BIGINT,
    cid BIGINT,
    sent BIGINT --timestamp
);

CREATE TABLE IF NOT EXISTS blacklist (
    id BIGINT PRIMARY KEY,
    added_by BIGINT,
    reason TEXT NOT NULL,
    added_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT NULL -- Optional kwarg that would only blacklist the user for a specific amount of time
);