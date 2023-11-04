CREATE EXTENSION "uuid-ossp";

CREATE TYPE user_role AS ENUM ('Admin', 'Contestant', 'Organiser');

CREATE TABLE users (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    role            user_role       NOT NULL,
    username        VARCHAR(32)     NOT NULL CHECK (LENGTH(username) > 3) UNIQUE,
    image           BYTEA,
    password        TEXT            NOT NULL,
    email           VARCHAR(128)    NOT NULL CHECK (LENGTH(username) > 4) UNIQUE,
    name            VARCHAR(64)     NOT NULL,
    surname         VARCHAR(64)     NOT NULL,
    is_verified     BOOLEAN         NOT NULL
);

CREATE TABLE problems (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    name            TEXT            NOT NULL,
    example_input   TEXT            NOT NULL,
    example_output  TEXT            NOT NULL,
    is_hidden       BOOLEAN         NOT NULL,
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0),
    runtime_limit   TIME            NOT NULL,
    description     TEXT            NOT NULL,
    tests_dir       TEXT            NOT NULL,
    is_private      BOOLEAN         NOT NULL
);

CREATE TABLE competition (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    name            TEXT            NOT NULL,
    description     TEXT            NOT NULL,
    start_time      TIMESTAMP       NOT NULL,
    end_time        TIMESTAMP       NOT NULL,
    parentId        UUID            NOT NULL REFERENCES competition(id),
    problems        UUID[]
);

CREATE TABLE competition_participations (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id),
    competition_id  UUID            NOT NULL REFERENCES competition(id),
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0)
);

CREATE TABLE problems_on_competitions (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    problem_id      UUID            NOT NULL REFERENCES problems(id),
    competition_id  UUID            NOT NULL REFERENCES competition(id),
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0)
);

CREATE TABLE problem_result (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    problem_id      UUID            NOT NULL REFERENCES problems(id),
    competition_id  UUID            NOT NULL REFERENCES competition(id),
    user_id         UUID            NOT NULL REFERENCES users(id),
    average_runtime TIME            NOT NULL,
    is_correct      BOOLEAN         NOT NULL,
    num_of_points   REAL            NOT NULL,
    source_code     TEXT            NOT NULL
);

CREATE TABLE trophies (
    id              UUID            NOT NULL UNIQUE PRIMARY KEY,
    competition_id  UUID            NOT NULL REFERENCES competition(id),
    user_id         UUID            NOT NULL REFERENCES users(id),
    position        SMALLINT        NOT NULL CHECK (position > 0)
    icon            BYTEA           NOT NULL
);
