import sqlite3

con = sqlite3.connect('cache.db')

# delete table from previous version
local_fields = set(f[1] for f in con.execute('PRAGMA table_info("local")').fetchall())
if 'mcBestagon' not in local_fields:
    con.execute('DROP TABLE IF EXISTS local')
    con.execute('DROP TABLE IF EXISTS community')
    print('found old version, deleting them')

# build tables if they don't exist
con.execute("""
CREATE TABLE IF NOT EXISTS "local" (
	"solution_file"		TEXT NOT NULL UNIQUE,
	"last_check"		INTEGER NOT NULL,
	"solution_name"		TEXT,
	"puzzle_name"		TEXT NOT NULL,
	"valid"				INTEGER NOT NULL,
	"omsimtime"			REAL,
	"mpCost"			INTEGER,
	"mpCycles"			INTEGER,
	"mpArea"			INTEGER,
	"mpInstructions"	INTEGER,
	"mcCost"			INTEGER,
	"mcCycles"			INTEGER,
	"mcArea"			INTEGER,
	"mcInstructions"	INTEGER,
	"mcHeight"			INTEGER,
	"mcWidth"			REAL,
	"mcBestagon"		INTEGER,
	"mcRate"			REAL,
	"mcAreaInfLevel"	INTEGER,
	"mcAreaInfValue"	INTEGER,
	"mcHeightInf"		INTEGER,
	"mcWidthInf"		REAL,
	"mcBestagonInf"		INTEGER,
	"mcTrackless"		INTEGER,
	"mcOverlap"			INTEGER,
	"mcLoop"			INTEGER,
	PRIMARY KEY("solution_file")
)	""")
con.execute("""
CREATE TABLE IF NOT EXISTS "community_cache" (
	"puzzle_name"		TEXT NOT NULL UNIQUE,
	"last_check"		INTEGER NOT NULL,
	PRIMARY KEY("puzzle_name")
)	""")
con.execute("""
CREATE TABLE IF NOT EXISTS "community" (
	"solution_file"		TEXT NOT NULL UNIQUE,
	"gif_file"			TEXT,
	"puzzle_name"		TEXT NOT NULL,
	"category"			TEXT,
	"mCost"				INTEGER,
	"mCycles"			INTEGER,
	"mArea"				INTEGER,
	"mInstructions"		INTEGER,
	"mHeight"			INTEGER,
	"mWidth"			REAL,
	"mBestagon"			INTEGER,
	"mRate"				REAL,
	"mAreaInfLevel"		INTEGER,
	"mAreaInfValue"		INTEGER,
	"mHeightInf"		INTEGER,
	"mWidthInf"			REAL,
	"mBestagonInf"		INTEGER,
	"mTrackless"		INTEGER,
	"mOverlap"			INTEGER,
	"mLoop"			INTEGER,
	PRIMARY KEY("solution_file")
)	""")
con.execute("""CREATE INDEX IF NOT EXISTS "community_puzzle_name" ON "community" ( "puzzle_name" )""")
con.execute("""CREATE INDEX IF NOT EXISTS "local_puzzle_name" ON "local" ( "puzzle_name" )""")
con.commit()
