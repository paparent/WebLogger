DROP TABLE IF EXISTS entries;
CREATE TABLE entries (
	id integer primary key autoincrement,
	host text not null,
	user text,
	timestamp integer not null,
	method text not null,
	url text not null,
	headers text not null,
	payload text
);
