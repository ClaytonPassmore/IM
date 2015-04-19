CREATE DATABASE IM;

USE IM;

CREATE TABLE USERS (
    id bigint NOT NULL AUTO_INCREMENT UNIQUE,
    username varchar(255) NOT NULL,
    password varchar(255) NOT NULL,
    active bool DEFAULT FALSE,
    last_seen_at timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);
