import os
import io
import re
import sys
import json
import time
import asyncio
import tempfile
import textwrap
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

try:
    from groq import Groq
except Exception:
    Groq = None


DEFAULT_TASKS: List[Dict[str, Any]] = [
    {
        "id": "two_sum",
        "prompt": (
            "Write a Python function `two_sum(nums: list[int], target: int) -> list[int]` "
            "that returns the indices of the two numbers in `nums` that add up to `target`. "
            "Assume exactly one solution exists. Return only the function definition."
        ),
        "tests": [
            "assert sorted(two_sum([2,7,11,15], 9)) == [0,1]",
            "assert sorted(two_sum([3,2,4], 6)) == [1,2]",
            "assert sorted(two_sum([3,3], 6)) == [0,1]",
        ],
    },
    {
        "id": "is_palindrome",
        "prompt": (
            "Write a Python function `is_palindrome(s: str) -> bool` that returns True if "
            "`s` is a palindrome ignoring case and non-alphanumeric chars. Return only the "
            "function definition."
        ),
        "tests": [
            "assert is_palindrome('A man, a plan, a canal: Panama') is True",
            "assert is_palindrome('race a car') is False",
            "assert is_palindrome('') is True",
        ],
    },
    {
        "id": "longest_substr",
        "prompt": (
            "Write a Python function `longest_unique_substr(s: str) -> int` that returns the "
            "length of the longest substring without repeating characters. Return only the "
            "function definition."
        ),
        "tests": [
            "assert longest_unique_substr('abcabcbb') == 3",
            "assert longest_unique_substr('bbbbb') == 1",
            "assert longest_unique_substr('pwwkew') == 3",
        ],
    },
    {
        "id": "merge_intervals",
        "prompt": (
            "Write a Python function `merge_intervals(intervals: list[list[int]]) -> list[list[int]]` "
            "that merges overlapping intervals and returns them sorted. Return only the function definition."
        ),
        "tests": [
            "assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]",
            "assert merge_intervals([[1,4],[4,5]]) == [[1,5]]",
            "assert merge_intervals([]) == []",
        ],
    },
    {
        "id": "binary_search",
        "prompt": (
            "Write a Python function `binary_search(arr: list[int], target: int) -> int` that returns "
            "the index of `target` in sorted `arr`, or -1 if not found. Return only the function definition."
        ),
        "tests": [
            "assert binary_search([1,2,3,4,5], 3) == 2",
            "assert binary_search([1,2,3,4,5], 6) == -1",
            "assert binary_search([], 1) == -1",
        ],
    },
]


CODE_BLOCK_RE = re.compile(r"```(?:python)?\s*(.*?)```", re.DOTALL)


def _extract_code(text: str) -> str:
    if not text:
        return ""
    m = CODE_BLOCK_RE.search(text)
    if m:
        return m.group(1).strip()
    return text.strip()


def _run_in_subprocess(code: str, tests: List[str], timeout: float = 6.0) -> Dict[str, Any]:
    full = code + "\n\n" + "\n".join(tests) + "\n"
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as tf:
        tf.write(full)
        path = tf.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout,
        )
        return {
            "passed": proc.returncode == 0,
            "stdout": proc.stdout[-2000:],
            "stderr": proc.stderr[-2000:],
            "returncode": proc.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"passed": False, "stdout": "", "stderr": "TIMEOUT", "returncode": -1}
    except Exception as e:
        return {"passed": False, "stdout": "", "stderr": str(e), "returncode": -2}
    finally:
        try:
            os.unlink(path)
        except Exception:
            pass


class SelfBenchmark:
    """
    Lightweight HumanEval-style self-evaluation. Runs APEX's models on small
    coding tasks, validates by executing tests in a subprocess, and tracks
    pass-rate over time. Used to catch capability regressions after self-edits.
    """

    def __init__(self, data_dir: str = "data/forge", console=None,
                 tasks: Optional[List[Dict[str, Any]]] = None,
                 timeout_sec: float = 6.0):
        load_dotenv()
        self.console = console
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bench_path = self.data_dir / "bench.json"
        self.tasks = tasks or DEFAULT_TASKS
        self.timeout_sec = timeout_sec

        gkey = os.getenv("GEMINI_API_KEY")
        self.gemini = genai.Client(api_key=gkey) if (genai and gkey) else None

        qkey = os.getenv("GROQ_API_KEY")
        self.groq = Groq(api_key=qkey) if (Groq and qkey) else None

    def _log(self, msg: str, level: str = "info"):
        if not self.console:
            return
        color = {"info": "green", "warn": "yellow", "err": "red"}.get(level, "white")
        self.console.print(f"[dim {color}][Bench] {msg}[/dim {color}]")

    async def _gemini_complete(self, prompt: str, model: str) -> str:
        if not self.gemini:
            return ""
        try:
            res = await asyncio.to_thread(
                self.gemini.models.generate_content,
                model=model,
                contents=prompt,
            )
            return res.text or ""
        except Exception as e:
            self._log(f"gemini {model} fail: {e}", level="warn")
            return ""

    async def _groq_complete(self, prompt: str, model: str) -> str:
        if not self.groq:
            return ""
        try:
            res = await asyncio.to_thread(
                self.groq.chat.completions.create,
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=900,
            )
            return res.choices[0].message.content or ""
        except Exception as e:
            self._log(f"groq {model} fail: {e}", level="warn")
            return ""

    async def run_task(self, task: Dict[str, Any], model_label: str, model_id: str, provider: str) -> Dict[str, Any]:
        prompt = task["prompt"]
        t0 = time.time()
        if provider == "gemini":
            text = await self._gemini_complete(prompt, model_id)
        elif provider == "groq":
            text = await self._groq_complete(prompt, model_id)
        else:
            text = ""
        latency = time.time() - t0
        code = _extract_code(text)
        if not code:
            return {
                "task": task["id"], "model": model_label, "provider": provider,
                "latency": round(latency, 3), "passed": False, "error": "no_code",
            }
        result = await asyncio.to_thread(_run_in_subprocess, code, task["tests"], self.timeout_sec)
        return {
            "task": task["id"],
            "model": model_label,
            "provider": provider,
            "latency": round(latency, 3),
            "passed": result["passed"],
            "error": "" if result["passed"] else (result["stderr"][:240] or "fail"),
        }

    async def run(self, models: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        if models is None:
            models = []
            if self.gemini:
                models.append({"label": "gemini-2.5-flash", "id": "gemini-2.5-flash", "provider": "gemini"})
                models.append({"label": "gemini-2.5-flash-lite", "id": "gemini-2.5-flash-lite", "provider": "gemini"})
            if self.groq:
                models.append({"label": "groq-llama-3.1-8b", "id": "llama-3.1-8b-instant", "provider": "groq"})

        if not models:
            self._log("no models configured (missing API keys)", level="warn")
            return {"ts": datetime.now().isoformat(), "results": [], "summary": {}}

        results: List[Dict[str, Any]] = []
        for m in models:
            for task in self.tasks:
                r = await self.run_task(task, m["label"], m["id"], m["provider"])
                results.append(r)

        summary: Dict[str, Dict[str, Any]] = {}
        for m in models:
            label = m["label"]
            mres = [r for r in results if r["model"] == label]
            passed = sum(1 for r in mres if r["passed"])
            total = len(mres)
            avg_lat = round(sum(r["latency"] for r in mres) / max(total, 1), 3)
            summary[label] = {
                "pass_rate": round(passed / total, 3) if total else 0.0,
                "passed": passed,
                "total": total,
                "avg_latency_sec": avg_lat,
            }

        record = {
            "ts": datetime.now().isoformat(),
            "results": results,
            "summary": summary,
        }
        self._persist(record)
        self._log(f"bench done: {summary}", level="info")
        return record

    def _persist(self, record: Dict[str, Any]):
        try:
            existing = []
            if self.bench_path.exists():
                existing = json.loads(self.bench_path.read_text(encoding="utf-8"))
            existing.append(record)
            existing = existing[-50:]
            self.bench_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
        except Exception as e:
            self._log(f"persist fail: {e}", level="warn")

    def history(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.bench_path.exists():
            return []
        try:
            return json.loads(self.bench_path.read_text(encoding="utf-8"))[-limit:]
        except Exception:
            return []

    def regression_check(self, drop_threshold: float = 0.15) -> Dict[str, Any]:
        hist = self.history(limit=2)
        if len(hist) < 2:
            return {"regression": False, "reason": "insufficient_history"}
        prev, cur = hist[-2]["summary"], hist[-1]["summary"]
        regressions = []
        for label, cur_stats in cur.items():
            if label not in prev:
                continue
            delta = cur_stats["pass_rate"] - prev[label]["pass_rate"]
            if delta <= -drop_threshold:
                regressions.append({"model": label, "delta": round(delta, 3),
                                    "prev": prev[label]["pass_rate"], "cur": cur_stats["pass_rate"]})
        return {"regression": bool(regressions), "details": regressions, "checked_at": datetime.now().isoformat()}
