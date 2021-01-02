# INTLog

INTLog is a simple Flask app designed to keep track of potentially interesting artifacts during an investigation. 

This application was designed to help me keep track of artifacts that I may stumble across during an investigation. I was originally using things like notepad, maltego, jupyter, and a bunch of other apps. The problem I ran into is that I needed a simple wheel, not a nuclear reactor to log what I was seeing. Secondly, I wanted something that could be hosted locally and data kept on my disk. And just like that, INTLog was born. Simplicity is the name of the game here. This app caters specifically to my needs and maybe it will help you too.

This project is in an EXTREMELY early stage. Stuff is likely terrible.

**TODO:**

- Support pagination
- Likely fix things
- Export to JSON
- Clean up templates
- Contemplate existence
- Drink coffee

## Setup

Setup env: 

```
INTLog » python3 -m venv env
INTLog » source env/bin/activate
```

Install requirements: `pip3 install -r requirements.txt`

### Setup SQLite

Create a new SQLite db within the `data` directory named `intlog.sqlite`

**Setup the investigations table:**

```
CREATE TABLE investigations (
  id integer PRIMARY KEY AUTOINCREMENT NOT NULL,
  investigation_name varchar(128),
  investigation_date timestamp(128),
  investigation_desc text(250)
)
```

**Setup the artifacts table:**

```
CREATE TABLE "artifacts" (
	"id"	integer NOT NULL,
	"investigation_id"	integer(128),
	"artifact_name"	char(128),
	"artifact_type"	char(128),
	"artifact_desc"	varchar(250),
	"artifact_reference"	varchar(250),
	"artifact_date"	timestamp(128),
	PRIMARY KEY("id" AUTOINCREMENT),
	FOREIGN KEY("investigation_id") REFERENCES "investigations"("id")
)
```

## Screenshots

Index page: 

![](git_images/index.png)

Viewing an investigation (note: this is just simulated and random data for testing): 

![](git_images/investigation.png)