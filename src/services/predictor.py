import os
import sqlite3
import datetime
import hashlib
import json
import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple

class PredictorService:
    """
    APEX Predictive Intelligence Layer.
    Uses local SQLite for telemetry, scikit-learn for user behavior modeling,
    and rolling heuristics for anomaly detection and calendar tracking.
    """
    def __init__(self, db_path: str = ".apex/predictor.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
        self.cost_threshold = 5.00  # Default $5.00 spend warning
        
    def _init_db(self):
        """Initialize the SQLite tables for telemetry, budget, and deadlines."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Telemetry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS command_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                command TEXT,
                working_dir TEXT,
                exit_code INTEGER,
                execution_time REAL
            )
        """)
        
        # Spend tracker table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_spend (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                cost REAL,
                tokens_in INTEGER,
                tokens_out INTEGER,
                model_used TEXT
            )
        """)

        # Deadlines table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deadlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                due_date TEXT,
                risk REAL DEFAULT 0.0,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        conn.commit()
        conn.close()

    # ── 1. Telemetry & User Pattern Predictor ─────────────────────────────────

    def record_command(self, command: str, working_dir: str, exit_code: int, execution_time: float):
        """Record command execution to history."""
        # Clean command formatting
        command = command.strip()
        if not command:
            return
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO command_history (command, working_dir, exit_code, execution_time) VALUES (?, ?, ?, ?)",
            (command, working_dir, exit_code, execution_time)
        )
        conn.commit()
        conn.close()

    def predict_next_command(self, current_dir: str) -> Tuple[Optional[str], float]:
        """
        Predict the next command using scikit-learn DecisionTreeClassifier.
        Falls back to transition frequency if data is sparse or only 1 class exists.
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT timestamp, command, working_dir FROM command_history ORDER BY id DESC LIMIT 500", conn)
        conn.close()

        if len(df) < 5:
            # Not enough data for prediction
            return None, 0.0

        # Sort chronological (oldest first)
        df = df.iloc[::-1].reset_index(drop=True)

        # Feature extraction
        df["dt"] = pd.to_datetime(df["timestamp"])
        df["hour"] = df["dt"].dt.hour
        df["dayofweek"] = df["dt"].dt.dayofweek
        
        # Label encode commands and directories
        df["cmd_code"] = df["command"].astype("category").cat.codes
        df["dir_code"] = df["working_dir"].astype("category").cat.codes

        # We want to predict the next command code based on:
        # current command code, current directory code, hour of day, day of week
        df["prev_cmd_code"] = df["cmd_code"].shift(1)
        df["prev_dir_code"] = df["dir_code"].shift(1)

        # Drop first row because it has NaN shift
        df_clean = df.dropna().copy()
        
        # Check distinct target classes
        unique_targets = df_clean["command"].nunique()
        if unique_targets < 2:
            # Fallback: return the most common command (frequency-based)
            most_freq = df["command"].mode()
            if not most_freq.empty:
                return most_freq.iloc[0], 0.5
            return None, 0.0

        try:
            from sklearn.tree import DecisionTreeClassifier
            X = df_clean[["prev_cmd_code", "dir_code", "hour", "dayofweek"]].values
            y = df_clean["cmd_code"].values

            clf = DecisionTreeClassifier(max_depth=4, random_state=42)
            clf.fit(X, y)

            # Build feature vector for the prediction
            # Last executed command
            last_cmd_code = df["cmd_code"].iloc[-1]
            current_dir_code = df["dir_code"].iloc[-1] # fallback to last directory
            
            # Find category code matching current directory
            dir_cat = df["working_dir"].astype("category").cat.categories
            if current_dir in dir_cat:
                current_dir_code = dir_cat.get_loc(current_dir)
                
            now = datetime.datetime.now()
            current_hour = now.hour
            current_day = now.weekday()

            pred_features = np.array([[last_cmd_code, current_dir_code, current_hour, current_day]])
            pred_code = clf.predict(pred_features)[0]
            
            # Map code back to command string
            cmd_cat = df["command"].astype("category").cat.categories
            predicted_cmd = cmd_cat[pred_code]
            
            # Calculate simple confidence (e.g. probability)
            probs = clf.predict_proba(pred_features)[0]
            confidence = float(np.max(probs))

            return predicted_cmd, confidence
        except Exception:
            # In case sklearn fails or throws exception, fallback to simple bigram frequency
            last_cmd = df["command"].iloc[-1]
            bigrams = zip(df["command"][:-1], df["command"][1:])
            matches = [b[1] for b in bigrams if b[0] == last_cmd]
            if matches:
                from collections import Counter
                counts = Counter(matches)
                most_common, freq = counts.most_common(1)[0]
                return most_common, freq / len(matches)
            
            return df["command"].mode().iloc[0], 0.3

    # ── 2. Intent Autocomplete Engine ─────────────────────────────────────────

    def get_completion_suggestions(self, partial_input: str) -> List[str]:
        """Suggest completions matching prefix or similar historical entries."""
        if not partial_input:
            return []
            
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT command FROM command_history ORDER BY id DESC")
        commands = [row[0] for row in cursor.fetchall()]
        conn.close()

        # Prefix matching
        prefix_matches = [cmd for cmd in commands if cmd.lower().startswith(partial_input.lower())]
        
        # Substring matching (up to 5 items total)
        substring_matches = [cmd for cmd in commands if partial_input.lower() in cmd.lower() and cmd not in prefix_matches]
        
        suggestions = (prefix_matches + substring_matches)[:5]
        return suggestions

    # ── 3. Proactive Pre-fetching ─────────────────────────────────────────────

    def get_prefetch_candidates(self, predicted_command: str) -> Dict[str, Any]:
        """
        Determine context files to load proactively based on predicted command.
        """
        candidates = {
            "files": [],
            "error_logs": []
        }
        
        if not predicted_command:
            return candidates

        # Scan for common patterns in predicted command
        # For example, if we see a file path in the command, prefetch it
        import re
        file_matches = re.findall(r"[\w\.\-/\\]+\.(?:pdf|png|jpg|jpeg|webp|md|py|txt|json)", predicted_command)
        for f in file_matches:
            if os.path.exists(f):
                candidates["files"].append(os.path.abspath(f))

        # If it runs python tests, prefetch the test file
        if "pytest" in predicted_command or "python -m pytest" in predicted_command:
            test_files = re.findall(r"tests/[\w\-]+\.py", predicted_command)
            for tf in test_files:
                if os.path.exists(tf):
                    candidates["files"].append(os.path.abspath(tf))

        # Check for recent failures/errors in command history to attach logs
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT command, exit_code FROM command_history ORDER BY id DESC LIMIT 5")
        recent = cursor.fetchall()
        conn.close()

        for cmd, code in recent:
            if code != 0:
                # If there was a recent failure, pre-fetch its log or path if available
                candidates["error_logs"].append({
                    "command": cmd,
                    "exit_code": code,
                    "info": f"Command '{cmd}' failed recently with exit code {code}."
                })
                break

        return candidates

    # ── 4. Rolling Budget Anomaly Detection ───────────────────────────────────

    def record_spend(self, cost: float, tokens_in: int, tokens_out: int, model: str):
        """Record API spend transaction."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO api_spend (cost, tokens_in, tokens_out, model_used) VALUES (?, ?, ?, ?)",
            (cost, tokens_in, tokens_out, model)
        )
        conn.commit()
        conn.close()

    def check_budget_anomaly(self, current_cost: float) -> Tuple[bool, str]:
        """
        Check if the current interaction cost is an anomaly.
        Uses rolling mean + 2 std deviations of past spends.
        """
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT cost FROM api_spend ORDER BY id DESC LIMIT 100", conn)
        conn.close()

        if len(df) < 10:
            # Sparse data, only check against flat threshold
            if current_cost > 1.00:
                return True, f"Cost ${current_cost:.4f} exceeds flat threshold of $1.00."
            return False, ""

        mean = df["cost"].mean()
        std = df["cost"].std()
        
        # Handle case where standard deviation is zero or NaN
        if pd.isna(std) or std == 0.0:
            std = 0.05
            
        threshold = mean + 2 * std
        if current_cost > threshold:
            return True, f"Anomalous cost detected: ${current_cost:.4f} exceeds rolling limit of ${threshold:.4f} (mean=${mean:.4f}, std=${std:.4f})."
        return False, ""

    def get_spend_summary(self) -> Dict[str, Any]:
        """Get daily spend totals and budget health metrics."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Today's total spend
        cursor.execute("""
            SELECT SUM(cost), COUNT(id) FROM api_spend 
            WHERE date(timestamp) = date('now')
        """)
        today_cost, today_calls = cursor.fetchone()
        today_cost = today_cost or 0.0
        today_calls = today_calls or 0

        # Overall total spend
        cursor.execute("SELECT SUM(cost) FROM api_spend")
        total_cost = cursor.fetchone()[0] or 0.0
        
        conn.close()
        
        return {
            "today_cost": today_cost,
            "today_calls": today_calls,
            "total_cost": total_cost,
            "cost_threshold": self.cost_threshold,
            "percent_exhausted": min(100.0, (today_cost / self.cost_threshold) * 100.0)
        }

    # ── 5. Calendar & Deadline Tracker ────────────────────────────────────────

    def sync_deadlines(self, project_todos: List[Dict[str, Any]]):
        """
        Parse todo items or comments for deadlines and update deadlines DB.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Clear existing deadlines first
        cursor.execute("DELETE FROM deadlines WHERE status = 'pending'")
        
        import re
        date_pattern = re.compile(r"due:?\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE)
        
        for item in project_todos:
            text = item.get("task", "") or item.get("text", "") or item.get("description", "")
            if not text:
                continue
            
            match = date_pattern.search(text)
            if match:
                due_date = match.group(1)
                cursor.execute(
                    "INSERT INTO deadlines (task, due_date, risk) VALUES (?, ?, ?)",
                    (text, due_date, 0.1)
                )
                
        conn.commit()
        conn.close()

    def get_upcoming_deadlines(self, days_window: int = 2) -> List[Dict[str, Any]]:
        """Get deadlines due within specified days window."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Select pending deadlines
        cursor.execute("SELECT task, due_date, risk FROM deadlines WHERE status = 'pending'")
        rows = cursor.fetchall()
        conn.close()

        upcoming = []
        now = datetime.date.today()
        for task, due_str, risk in rows:
            try:
                due_date = datetime.datetime.strptime(due_str, "%Y-%m-%d").date()
                days_left = (due_date - now).days
                if 0 <= days_left <= days_window:
                    upcoming.append({
                        "task": task,
                        "due_date": due_str,
                        "days_left": days_left,
                        "risk": risk + (0.4 if days_left <= 1 else 0.1)  # risk amplifies close to due date
                    })
            except Exception:
                pass
                
        return upcoming
