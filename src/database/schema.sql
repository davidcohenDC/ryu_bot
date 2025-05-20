CREATE TABLE IF NOT EXISTS tournaments
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id     INTEGER   NOT NULL,
    name          TEXT      NOT NULL,
    code          TEXT,
    format        TEXT      NOT NULL,

    swiss         INTEGER   NOT NULL DEFAULT 0,
    top_cut       INTEGER   NOT NULL DEFAULT 0,
    current_round INTEGER   NOT NULL DEFAULT 0,
    is_deleted    INTEGER   NOT NULL DEFAULT 0,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tournaments (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  code TEXT,
  game_format TEXT NOT NULL,
  active_phase_index INTEGER NOT NULL DEFAULT 0,
  active_round_index INTEGER NOT NULL DEFAULT 0,
  is_deleted INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT
);

CREATE TABLE phases (
  tournament_id INTEGER NOT NULL REFERENCES tournaments(id),
  phase_order  INTEGER NOT NULL,
  type         TEXT NOT NULL,
  rounds       INTEGER NOT NULL,
  mode         TEXT NOT NULL,
  PRIMARY KEY (tournament_id, phase_order)
);

CREATE TABLE contexts (
  tournament_id INTEGER PRIMARY KEY REFERENCES tournaments(id),
  guild_id      INTEGER NOT NULL
);
