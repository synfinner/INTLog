#!/usr/bin/env python3

import sqlite3

conn = sqlite3.connect('data/intlog.sqlite')

c = conn.cursor()

# Create Investigations table
c.execute(''' CREATE TABLE investigations (
  id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  investigation_name varchar(128),
  investigation_date timestamp(128),
  investigation_desc text(250)
)''')

# Create Artifacts table
c.execute('''CREATE TABLE "artifacts" (
    "id"    integer NOT NULL,
    "investigation_id"  integer(128),
    "artifact_name" char(128),
    "artifact_type" char(128),
    "artifact_desc" varchar(250),
    "artifact_reference"    varchar(250),
    "artifact_date" timestamp(128),
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("investigation_id") REFERENCES "investigations"("id")
)''')

c.execute('''CREATE TABLE types (
  id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  type varchar(128)
)''')

c.execute("""INSERT INTO types (id, type) VALUES
(1, 'Mailing Address'),
(2, 'Misc'),
(3, 'Username'),
(4, 'URL'),
(5, 'TweetURL'),
(6, 'TwitterUser'),
(7, 'SHA256'),
(8, 'SHA1'),
(9, 'Organization'),
(10, 'MD5'),
(11, 'IP'),
(12, 'HumanName'),
(13, 'Domain'),
(14, 'CIDR');""")
conn.commit()