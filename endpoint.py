import os
import sqlite3
from typing import *
from datetime import datetime
from fastapi import FastAPI, Query, HTTPException

from config import ACCEPTED_DB_PATH, TABLE_NAME_ACCEPTED_DB, OVERALL_DB_PATH, TABLE_NAME_OVERALL_DB

app = FastAPI(title="Pencari Loker API", version="1.0.0")

def get_connection(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def ensure_db(db_path: str):
    if not os.path.exists(db_path):
        raise HTTPException(
            status_code=404, detail=f"Database not found at {db_path}")     


def fetch_stats(db_path: str, table_name: str) -> dict:
    ensure_db(db_path)
    conn = None
    try:
        conn = get_connection(db_path)
        query = f"""
            SELECT 
                COUNT(*) AS total,
                COUNT(CASE WHEN Website_Loker = 'Disnakerja' THEN 1 END) AS total_disnaker,
                COUNT(CASE WHEN Website_Loker = 'Inginkerja' THEN 1 END) AS total_inginkerja,
                COUNT(CASE WHEN Website_Loker = 'RekrutmenBersama' THEN 1 END) AS total_rekrutmenbersama
            FROM {table_name}
        """
        row = conn.execute(query).fetchone()
        return {
            "total": row["total"],
            "detail": {
                "Disnakerja": row["total_disnaker"],
                "Inginkerja": row["total_inginkerja"],
                "RekrutmenBersama": row["total_rekrutmenbersama"],
            },
            "storage_size_bytes": os.path.getsize(db_path),
        }
    finally:
        if conn:
            conn.close()


def fetch_recent(db_path: str, table_name: str, limit: int, website_loker: str | None = None, from_date: str | None = None, to_date: str | None = None) -> dict:
    ensure_db(db_path)
    conn = None
    try:
        conn = get_connection(db_path)
        
        conditions = []
        params = []
        
        if website_loker:
            conditions.append("Website_Loker = ?")
            params.append(website_loker)
            
        # Handle from_date
        if from_date:
            try:
                db_from_date = datetime.strptime(from_date, "%d-%m-%Y").strftime("%Y-%m-%d")
                conditions.append("SUBSTR(Last_Updated, 1, 10) >= ?") 
                params.append(db_from_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid from_date format. Use 'dd-mm-yyyy'.")
                
        # Handle to_date (NEW)
        if to_date:
            try:
                db_to_date = datetime.strptime(to_date, "%d-%m-%Y").strftime("%Y-%m-%d")
                conditions.append("SUBSTR(Last_Updated, 1, 10) <= ?") 
                params.append(db_to_date)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid to_date format. Use 'dd-mm-yyyy'.")

        where_clause = ""
        if conditions:
            where_clause = "WHERE " + " AND ".join(conditions)
            
        params.append(limit)
        
        query = f"SELECT * FROM {table_name} {where_clause} ORDER BY Last_Updated DESC LIMIT ?"
        
        rows = conn.execute(query, params).fetchall()
        return {"items": [dict(r) for r in rows]}
    finally:
        if conn:
            conn.close()


@app.get("/")
def root():
    return {
        "message": "Welcome to the Pencari Loker API. Visit /docs for API documentation. Good luck on your job search!"
    }

@app.get("/health")
def health():
    return {"status": "ok"}

# ENDPOINTS for selected
@app.get("/selected/stats")
def get_selected_stats():
    """Get statistics for accepted vacancies."""
    return fetch_stats(ACCEPTED_DB_PATH, TABLE_NAME_ACCEPTED_DB)

@app.get("/selected/recent")
def get_selected_recent(limit: int = Query(10, ge=1, le=200), website_loker: str | None = Query(None), from_date: str | None = Query(None), to_date: str | None = Query(None)):
    """Get the most recent accepted vacancies."""
    return fetch_recent(ACCEPTED_DB_PATH, TABLE_NAME_ACCEPTED_DB, limit, website_loker, from_date, to_date)


# Endpoints for All
@app.get("/all/stats")
def get_all_stats():
    """Get statistics for all logged vacancies."""
    return fetch_stats(OVERALL_DB_PATH, TABLE_NAME_OVERALL_DB)

@app.get("/all/recent")
def get_all_recent(limit: int = Query(10, ge=1, le=200), website_loker: str | None = Query(None), from_date: str | None = Query(None), to_date: str | None = Query(None)):
    """Get the most recent items from all logged vacancies."""
    return fetch_recent(OVERALL_DB_PATH, TABLE_NAME_OVERALL_DB, limit, website_loker, from_date, to_date)