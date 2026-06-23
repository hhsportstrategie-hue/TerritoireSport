-- TerritoireSport — Schéma SQLite

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS clubs (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    sport           TEXT NOT NULL,
    city            TEXT NOT NULL,
    department      TEXT NOT NULL,
    region          TEXT DEFAULT 'Normandie',
    size            TEXT NOT NULL,   -- 'micro' | 'small' | 'medium' | 'large'
    members_count   INTEGER DEFAULT 0,
    description     TEXT,
    website         TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS diagnostics (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    answers         TEXT NOT NULL,   -- JSON
    score           INTEGER NOT NULL,
    profile         TEXT NOT NULL,   -- 'pioneer' | 'engaged' | 'emerging' | 'starter'
    completed_at    TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS club_projects (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    project_id      TEXT NOT NULL,   -- référence à projects_library.json
    status          TEXT DEFAULT 'idea',  -- 'idea' | 'planning' | 'active' | 'done'
    notes           TEXT,
    started_at      TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS partners (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,   -- 'public' | 'association' | 'company'
    category        TEXT NOT NULL,   -- thématique
    city            TEXT,
    department      TEXT,
    contact_email   TEXT,
    contact_url     TEXT,
    description     TEXT,
    themes          TEXT NOT NULL    -- JSON array de thématiques
);

CREATE INDEX IF NOT EXISTS idx_diagnostics_club ON diagnostics(club_id);
CREATE INDEX IF NOT EXISTS idx_club_projects_club ON club_projects(club_id);
CREATE INDEX IF NOT EXISTS idx_partners_dept ON partners(department);
