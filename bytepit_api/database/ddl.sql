CREATE EXTENSION "uuid-ossp";

CREATE TYPE user_role AS ENUM ('Admin', 'Contestant', 'Organiser');

CREATE TABLE users (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    role            user_role       NOT NULL,
    username        VARCHAR(32)     NOT NULL CHECK (LENGTH(username) > 3) UNIQUE,
    image           BYTEA,
    password_hash   VARCHAR(255)    NOT NULL,
    email           VARCHAR(128)    NOT NULL CHECK (LENGTH(email) > 4) UNIQUE,
    name            VARCHAR(64)     NOT NULL,
    surname         VARCHAR(64)     NOT NULL,
    is_verified     BOOLEAN         NOT NULL,
    created_on      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE INDEX index_users_email ON users (email);

CREATE TABLE problems (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    name            TEXT            NOT NULL,
    example_input   TEXT            NOT NULL,
    example_output  TEXT            NOT NULL,
    is_hidden       BOOLEAN         NOT NULL,
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0),
    runtime_limit   TIME            NOT NULL,
    description     TEXT            NOT NULL,
    tests_dir       TEXT            NOT NULL,
    is_private      BOOLEAN         NOT NULL,
    created_on      TIMESTAMP       NOT NULL DEFAULT NOW()
);

CREATE TABLE competition (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    name            TEXT            NOT NULL,
    description     TEXT            NOT NULL,
    start_time      TIMESTAMP       NOT NULL,
    end_time        TIMESTAMP       NOT NULL,
    parentId        UUID            NOT NULL REFERENCES competition(id) ON DELETE CASCADE,
    problems        UUID[]
);

CREATE TABLE competition_participations (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id         UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    competition_id  UUID            NOT NULL REFERENCES competition(id) ON DELETE CASCADE,
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0)
);

CREATE TABLE problems_on_competitions (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    problem_id      UUID            NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    competition_id  UUID            NOT NULL REFERENCES competition(id) ON DELETE CASCADE,
    num_of_points   REAL            NOT NULL CHECK (num_of_points > 0)
);

CREATE TABLE problem_result (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    problem_id      UUID            NOT NULL REFERENCES problems(id) ON DELETE CASCADE,
    competition_id  UUID            NOT NULL REFERENCES competition(id) ON DELETE CASCADE,
    user_id         UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    average_runtime TIME            NOT NULL,
    is_correct      BOOLEAN         NOT NULL,
    num_of_points   REAL            NOT NULL,
    source_code     TEXT            NOT NULL
);

CREATE TABLE trophies (
    id              uuid            DEFAULT uuid_generate_v4() PRIMARY KEY,
    competition_id  UUID            NOT NULL REFERENCES competition(id) ON DELETE CASCADE,
    user_id         UUID            NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    position        SMALLINT        NOT NULL CHECK (position > 0),
    icon            BYTEA           NOT NULL
);
