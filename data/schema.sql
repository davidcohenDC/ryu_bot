CREATE TABLE IF NOT EXISTS `warns` (
  `id` int(11) NOT NULL,
  `user_id` varchar(20) NOT NULL,
  `server_id` varchar(20) NOT NULL,
  `moderator_id` varchar(20) NOT NULL,
  `reason` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tournaments
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    server_id     INTEGER   NOT NULL,
    name          TEXT      NOT NULL,
    code          TEXT,
    swiss         INTEGER   NOT NULL DEFAULT 0,
    top_cut       INTEGER   NOT NULL DEFAULT 0,
    current_round INTEGER   NOT NULL DEFAULT 0,
    is_deleted    INTEGER   NOT NULL DEFAULT 0,
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)