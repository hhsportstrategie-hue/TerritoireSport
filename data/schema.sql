-- TerritoireSport — Schéma SQLite v2.1

PRAGMA foreign_keys = ON;

-- ── Clubs ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clubs (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    sport           TEXT NOT NULL,
    city            TEXT NOT NULL,
    department      TEXT NOT NULL,
    region          TEXT DEFAULT 'Normandie',
    size            TEXT NOT NULL,
    members_count   INTEGER DEFAULT 0,
    description     TEXT,
    website         TEXT,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ── Diagnostics club ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS diagnostics (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    answers         TEXT NOT NULL,
    score           INTEGER NOT NULL,
    profile         TEXT NOT NULL,
    completed_at    TEXT DEFAULT (datetime('now'))
);

-- ── Relation N-N club-territoire ─────────────────────────────
CREATE TABLE IF NOT EXISTS club_territories (
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    territory_id    TEXT NOT NULL,
    is_primary      BOOLEAN DEFAULT 0,
    PRIMARY KEY (club_id, territory_id)
);

-- ── Affinités club-territoire ────────────────────────────────
CREATE TABLE IF NOT EXISTS affinity_scores (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    theme_id        TEXT NOT NULL,
    score_sport     INTEGER DEFAULT 0,
    score_profil    INTEGER DEFAULT 0,
    score_taille    INTEGER DEFAULT 0,
    score_ressources INTEGER DEFAULT 0,
    score_total     INTEGER DEFAULT 0,
    rank            INTEGER,
    selected        BOOLEAN DEFAULT 0,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ── Projets en cours d'ingénierie ────────────────────────────
CREATE TABLE IF NOT EXISTS engineering_projects (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    inspiration_id  TEXT,
    theme_id        TEXT,
    public_cible    TEXT,
    objectifs       TEXT,
    activites       TEXT,
    ressources      TEXT,
    calendrier      TEXT,
    indicateurs     TEXT,
    status          TEXT DEFAULT 'draft',
    current_step    INTEGER DEFAULT 1,
    created_at      TEXT DEFAULT (datetime('now')),
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ── Suivi avancement template ────────────────────────────────
CREATE TABLE IF NOT EXISTS project_steps (
    id              TEXT PRIMARY KEY,
    project_id      TEXT NOT NULL REFERENCES engineering_projects(id) ON DELETE CASCADE,
    step_number     INTEGER,
    step_name       TEXT,
    completed       BOOLEAN DEFAULT 0,
    data            TEXT,
    completed_at    TEXT
);

-- ── Projets du club ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS club_projects (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    project_id      TEXT NOT NULL,
    status          TEXT DEFAULT 'idea',
    notes           TEXT,
    started_at      TEXT,
    updated_at      TEXT DEFAULT (datetime('now'))
);

-- ── Relation N-N projet-cas inspirants ───────────────────────
CREATE TABLE IF NOT EXISTS project_inspirations (
    project_id      TEXT NOT NULL REFERENCES engineering_projects(id) ON DELETE CASCADE,
    cas_id          TEXT NOT NULL,
    PRIMARY KEY (project_id, cas_id)
);

-- ── Partenaires ──────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS partners (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,
    category        TEXT NOT NULL,
    city            TEXT,
    department      TEXT,
    contact_email   TEXT,
    contact_url     TEXT,
    description     TEXT,
    themes          TEXT NOT NULL
);

-- ── Sources de financement (AAP) ─────────────────────────────
CREATE TABLE IF NOT EXISTS funding_sources (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,
    organization    TEXT NOT NULL,
    themes          TEXT NOT NULL,
    amount_min      INTEGER,
    amount_max      INTEGER,
    deadline        TEXT,
    url             TEXT,
    description     TEXT,
    eligibility_criteria TEXT
);

-- ── Éligibilité club-AAP ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS club_funding_matches (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    project_id      TEXT REFERENCES engineering_projects(id) ON DELETE CASCADE,
    aap_id          TEXT NOT NULL REFERENCES funding_sources(id) ON DELETE CASCADE,
    score_eligibility INTEGER,
    eligible        BOOLEAN,
    reasons         TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ── Partenaires économiques adaptés ──────────────────────────
CREATE TABLE IF NOT EXISTS club_partner_matches (
    id              TEXT PRIMARY KEY,
    club_id         TEXT NOT NULL REFERENCES clubs(id) ON DELETE CASCADE,
    project_id      TEXT REFERENCES engineering_projects(id) ON DELETE CASCADE,
    partner_name    TEXT NOT NULL,
    partner_sector  TEXT,
    partner_size    TEXT,
    territory_id    TEXT,
    match_score     INTEGER,
    contact_info    TEXT,
    created_at      TEXT DEFAULT (datetime('now'))
);

-- ── Index ────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_diagnostics_club ON diagnostics(club_id);
CREATE INDEX IF NOT EXISTS idx_club_projects_club ON club_projects(club_id);
CREATE INDEX IF NOT EXISTS idx_partners_dept ON partners(department);
CREATE INDEX IF NOT EXISTS idx_affinity_club ON affinity_scores(club_id);
CREATE INDEX IF NOT EXISTS idx_engineering_club ON engineering_projects(club_id);
CREATE INDEX IF NOT EXISTS idx_funding_matches_club ON club_funding_matches(club_id);
CREATE INDEX IF NOT EXISTS idx_partner_matches_club ON club_partner_matches(club_id);