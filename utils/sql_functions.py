# Database functions ---------------
from config import ACCEPTED_DB_PATH, TABLE_NAME_ACCEPTED_DB, OVERALL_DB_PATH, TABLE_NAME_OVERALL_DB
from typing import List, Literal

import os
import sqlite3



def init_db() -> None:
    '''
    Initialize the sqlite database and create table if it doesn't exist
    '''
    # Make this dir if no exists
    if not os.path.exists("SQL_DATA"):
        os.makedirs("SQL_DATA")

    # DB for accepted vacancies
    with sqlite3.connect(ACCEPTED_DB_PATH) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME_ACCEPTED_DB} (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nama_Perusahaan TEXT,
                View_Count TEXT,
                Last_Updated TEXT,
                Location TEXT,
                Experience_Needed TEXT,
                Position TEXT,
                Reason TEXT,
                Post_link TEXT,
                Website_Loker TEXT
            )
            """
        )

        # Links are unique and it should be unique, if not i'm retarded
        conn.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{TABLE_NAME_ACCEPTED_DB}_link ON {TABLE_NAME_ACCEPTED_DB}(Post_link)"
        )

        conn.commit()

    # DB for all vacancies
    with sqlite3.connect(OVERALL_DB_PATH) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME_OVERALL_DB} (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nama_Perusahaan TEXT,
                View_Count TEXT,
                Last_Updated TEXT,
                Location TEXT,
                Experience_Needed TEXT,
                Position TEXT,
                Post_link TEXT,
                Website_Loker TEXT,
                DESCRIPTION TEXT
            )
            """
        )
        conn.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{TABLE_NAME_OVERALL_DB}_link ON {TABLE_NAME_OVERALL_DB}(Post_link)"
        )

        conn.commit()


def insert_rows(rows: List[dict], db_type: Literal["accepted", "overall"]) -> int:
    '''
    Insert multiple rows into the database by appending them from the bottom
    
    Parameters
    ----------
    - rows : List[dict]
        A list of dictionaries representing the rows to be inserted
    - db_type : Literal["accepted", "overall"]
        The type of database to insert into, either "accepted" for accepted vacancies or "overall" for all logged vacancies
    Returns
    -------
    - int
        The number of rows inserted
    '''
    if not rows:
        return 0

    rows = rows[::-1] # Reverse the list to insert the bottom rows first

    match db_type:
        case "accepted":
            # Insert rows into the database
            with sqlite3.connect(ACCEPTED_DB_PATH) as conn:
            # Updated insert statement
                conn.executemany(
                    f"""
                    INSERT OR IGNORE INTO {TABLE_NAME_ACCEPTED_DB}
                    (Nama_Perusahaan, View_Count, Last_Updated, Location, Experience_Needed, Position, Reason, Post_link, Website_Loker)
                    VALUES (:Nama_Perusahaan, :View_Count, :Last_Updated, :Location, :Experience_Needed, :Position, :Reason, :Post_link, :Website_Loker)
                    """,
                    rows,
                )
                conn.commit()
        case "overall":
            with sqlite3.connect(OVERALL_DB_PATH) as conn:
                conn.executemany(
                    f"""
                    INSERT OR IGNORE INTO {TABLE_NAME_OVERALL_DB}
                    (Nama_Perusahaan, View_Count, Last_Updated, Location, Experience_Needed, Position, Post_link, Website_Loker, DESCRIPTION)
                    VALUES (:Nama_Perusahaan, :View_Count, :Last_Updated, :Location, :Experience_Needed, :Position, :Post_link, :Website_Loker, :DESCRIPTION)
                    """,
                    rows,
                )
                conn.commit()
    
    return conn.total_changes
