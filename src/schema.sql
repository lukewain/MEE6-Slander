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

CREATE TABLE IF NOT EXISTS slander_targets (
    id BIGINT PRIMARY KEY,
    guild_id BIGINT, -- Will be a bigint (guild id) if the target is not global
    is_global BOOLEAN,
    bot BOOLEAN,
    nsfw BOOLEAN -- Can be overridden by the guild config if that is set to false
);

INSERT INTO slander_targets (id, is_global, bot, nsfw) VALUES (159985870458322944, TRUE, TRUE, TRUE), (1126230144273616966, TRUE, TRUE, TRUE) ON CONFLICT (id) DO NOTHING;