CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    manager_id INTEGER REFERENCES managers(manager_id),
    token TEXT NOT NULL DEFAULT UUID()
);