
PRAGMA foreign_keys = ON;

create table sensor (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    unit TEXT,
    name TEXT
);

create table sensor_float_data (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    val REAL,
    timestamp INTEGER,
    sensor_id INTEGER,
    FOREIGN KEY(sensor_id) REFERENCES sensor(id)
);

create table sensor_text_data (
    id  INTEGER PRIMARY KEY AUTOINCREMENT,
    val TEXT,
    timestamp INTEGER,
    sensor_id INTEGER,
    FOREIGN KEY(sensor_id) REFERENCES sensor(id)
);

create index sensor_float_date on sensor_float_data(timestamp);
