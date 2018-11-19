DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS profile;
DROP TABLE IF EXISTS recommendations;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE profile (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_id INTEGER UNIQUE NOT NULL,
  mal_username TEXT  NOT NULL,
  list TEXT NOT NULL,
  FOREIGN KEY (profile_id) REFERENCES user (id)
);

CREATE TABLE recommendations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  profile_id INTEGER NOT NULL,
  title TEXT UNIQUE NOT NULL,
  anime_type TEXT NOT NULL,
  episodes TEXT NOT NULL,
  studio TEXT NOT NULL,
  src TEXT NOT NULL,
  genre TEXT NOT NULL,
  score TEXT NOT NULL,
  synopsis TEXT NOT NULL,
  image_url TEXT NOT NULL,
  FOREIGN KEY (profile_id) REFERENCES user (id)
);