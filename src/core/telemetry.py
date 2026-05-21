import sqlite3
import os
import time
from datetime import datetime
from typing import Dict, Any, List

class SpendTracker:
    """
    Logs and tracks token usage and estimated costs.
    """
    def __init__(self, db_path: str = "data/apex.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        
        # 2026 Estimated Pricing (per 1M tokens)
        self.pricing = {
            "gemini-2.5-flash": {"in": 0.12, "out": 0.45},
            "gemini-2.5-flash-lite": {"in": 0.06, "out": 0.18},
            "gemini-1.5-pro": {"in": 1.25, "out": 5.00},
            "llama-3.1-8b-instant": {"in": 0.05, "out": 0.08},
            "llama-3.1-70b-versatile": {"in": 0.59, "out": 0.79}
        }

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS spend_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                session_id TEXT,
                model TEXT,
                tokens_in INTEGER,
                tokens_out INTEGER,
                estimated_cost REAL,
                compute_sec REAL,
                system_load REAL
            )
        """)
        conn.commit()
        conn.close()

    def log_interaction(self, session_id: str, model: str, tokens_in: int, tokens_out: int, compute_sec: float = 0.0, system_load: float = 0.0):
        timestamp = datetime.now().isoformat()
        
        # Calculate cost
        price = self.pricing.get(model, {"in": 0.5, "out": 1.5})
        token_cost = (tokens_in / 1_000_000 * price["in"]) + (tokens_out / 1_000_000 * price["out"])
        
        # Estimate local compute cost (electricity/hardware wear)
        # Assuming 250W under load and $0.15/kWh -> ~$0.00001 per second
        energy_cost = compute_sec * 0.00001 
        total_cost = token_cost + energy_cost
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO spend_logs (timestamp, session_id, model, tokens_in, tokens_out, estimated_cost, compute_sec, system_load)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, session_id, model, tokens_in, tokens_out, total_cost, compute_sec, system_load))
        conn.commit()
        conn.close()

    def get_daily_spend(self) -> float:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(estimated_cost) FROM spend_logs WHERE timestamp LIKE ?", (f"{today}%",))
        result = cursor.fetchone()[0]
        conn.close()
        return result if result else 0.0

    def daily_call_count(self) -> int:
        today = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM spend_logs WHERE timestamp LIKE ?", (f"{today}%",))
        result = cursor.fetchone()[0]
        conn.close()
        return int(result or 0)
