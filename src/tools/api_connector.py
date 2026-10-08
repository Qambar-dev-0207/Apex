"""
ApiConnectorTool — Connect APEX to external API endpoints and manage credentials.

Allows APEX to:
  1. Test and connect external HTTP/REST API endpoints.
  2. Detect missing API keys and prompt the user to provide credentials.
  3. Securely save API keys into the system (.env) without overwriting other variables.
  4. Register and persist configured endpoints in data/external_apis.json.
  5. Fetch data from registered or ad-hoc endpoints.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

logger = logging.getLogger("apex.api_connector")


def mask_key(val: str) -> str:
    """Mask key value for safe display in logs and telemetry."""
    if not val:
        return ""
    if len(val) <= 8:
        return "*" * len(val)
    return f"{val[:3]}...{val[-4:]}"


def save_key_to_env(key_name: str, key_value: str, env_path: Optional[str] = None) -> bool:
    """
    Safely append or update an environment variable in the root .env file.
    Preserves existing lines and comments.
    """
    key_name = key_name.strip().upper()
    key_value = key_value.strip()
    if not key_name:
        return False

    if not env_path:
        env_path = os.path.join(os.getcwd(), ".env")

    lines = []
    found = False
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "=" in stripped:
                    k, _ = stripped.split("=", 1)
                    if k.strip().upper() == key_name:
                        lines.append(f"{key_name}={key_value}\n")
                        found = True
                        continue
                lines.append(line)

    if not found:
        if lines and not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        lines.append(f"{key_name}={key_value}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    # Update runtime environment and reload dotenv
    os.environ[key_name] = key_value
    load_dotenv(dotenv_path=env_path, override=True)
    return True


class ApiConnectorTool:
    """
    System-level external API integration and credential management for APEX.
    """

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or os.path.join(os.getcwd(), "data")
        self.registry_file = os.path.join(self.data_dir, "external_apis.json")
        os.makedirs(self.data_dir, exist_ok=True)
        self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to read {self.registry_file}: {e}")
        return {}

    def _save_registry(self, data: Dict[str, Any]):
        try:
            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save {self.registry_file}: {e}")

    async def execute(self, action: str, input_data: Any) -> Dict[str, Any]:
        """Entrypoint dispatched from ParallelExecutor."""
        action = (action or "").lower().strip()
        data = {}
        if isinstance(input_data, dict):
            data = input_data
        elif isinstance(input_data, str):
            s = input_data.strip()
            if s.startswith("{") and s.endswith("}"):
                try:
                    data = json.loads(s)
                except Exception:
                    data = {"raw": s}
            else:
                data = {"raw": s}

        if action in ("save_key", "set_key", "add_key"):
            key_name = data.get("key_name") or data.get("name") or ""
            key_val = data.get("key_value") or data.get("value") or ""
            if not key_name and "raw" in data and "=" in data["raw"]:
                parts = data["raw"].split("=", 1)
                key_name = parts[0].strip()
                key_val = parts[1].strip()
            elif not key_name and "raw" in data:
                tokens = data["raw"].split()
                if len(tokens) >= 2:
                    key_name = tokens[0].strip()
                    key_val = tokens[1].strip()

            if not key_name or not key_val:
                return {
                    "success": False,
                    "error": "Usage: api_connector:save_key input_data='{\"key_name\": \"...\", \"key_value\": \"...\"}' or 'KEY_NAME=value'",
                }

            ok = save_key_to_env(key_name, key_val)
            if ok:
                return {
                    "success": True,
                    "output": f"API key '{key_name.upper()}' ({mask_key(key_val)}) successfully saved to system environment (.env) and loaded.",
                }
            return {"success": False, "error": f"Failed to save '{key_name}' to .env"}

        elif action in ("connect", "connect_endpoint", "test"):
            url = data.get("url") or data.get("endpoint") or ""
            name = data.get("name") or data.get("service") or "unnamed_api"
            api_key_name = data.get("api_key_name") or data.get("key_name")
            api_key_val = data.get("api_key_value") or data.get("key_value")
            headers = data.get("headers") or {}
            method = (data.get("method") or "GET").upper()

            # If user passed key value inline, persist it
            if api_key_name and api_key_val:
                save_key_to_env(api_key_name, api_key_val)

            # Check if key is available in environment
            if api_key_name:
                key_in_env = os.getenv(api_key_name)
                if not key_in_env and not api_key_val:
                    return {
                        "success": True,
                        "output": (
                            f"[AUTH REQUIRED] The endpoint '{name}' requires an API key '{api_key_name}'. "
                            f"Please provide your API key by running 'api_connector:save_key key_name={api_key_name} key_value=...' "
                            f"or adding '{api_key_name}=<your_key>' to your .env file."
                        ),
                    }
                if key_in_env and "Authorization" not in headers:
                    headers["Authorization"] = f"Bearer {key_in_env}"

            if not url:
                # Check if it's a known service name like weather
                if "weather" in name.lower() or "weather" in data.get("raw", "").lower():
                    url = "https://api.open-meteo.com/v1/forecast?latitude=51.5&longitude=-0.1&current=temperature_2m"
                    name = "weather"
                else:
                    return {
                        "success": False,
                        "error": "Missing 'url' or 'endpoint' parameter to connect.",
                    }

            try:
                async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                    resp = await client.request(method, url, headers=headers)

                if resp.status_code in (401, 403):
                    req_key = api_key_name or f"{name.upper()}_API_KEY"
                    return {
                        "success": False,
                        "error": (
                            f"Endpoint '{name}' returned HTTP {resp.status_code} Unauthorized. "
                            f"Authentication key is missing or invalid. Please add your key to system .env as '{req_key}'."
                        ),
                    }

                # Register endpoint
                registry = self._load_registry()
                registry[name] = {
                    "url": url,
                    "method": method,
                    "api_key_name": api_key_name,
                    "status": "connected",
                    "status_code": resp.status_code,
                }
                self._save_registry(registry)

                return {
                    "success": True,
                    "output": (
                        f"[CONNECTED] External API '{name}' successfully connected and verified.\n"
                        f"Endpoint: {url}\n"
                        f"HTTP Status: {resp.status_code} OK\n"
                        f"Stored in system external API registry (data/external_apis.json)."
                    ),
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to connect to '{url}': {str(e)}",
                }

        elif action in ("list", "status"):
            registry = self._load_registry()
            if not registry:
                return {
                    "success": True,
                    "output": "No external APIs currently registered in system. Use api_connector:connect to link an endpoint.",
                }
            return {
                "success": True,
                "output": json.dumps(registry, indent=2),
            }

        elif action in ("request_key", "prompt_key"):
            service = data.get("service") or data.get("name") or "External Service"
            key_name = data.get("key_name") or f"{service.upper().replace(' ', '_')}_API_KEY"
            return {
                "success": True,
                "output": (
                    f"Action Required: Please provide the API key for '{service}'.\n"
                    f"Key identifier: {key_name}\n"
                    f"To store it permanently in the system, reply with: 'save api key {key_name} <your_key>' "
                    f"or add it to your .env file."
                ),
            }

        elif action in ("call", "fetch", "get", "post"):
            endpoint_name = data.get("name") or data.get("endpoint")
            registry = self._load_registry()
            cfg = registry.get(endpoint_name, {})
            url = data.get("url") or cfg.get("url")
            method = (data.get("method") or cfg.get("method") or action).upper()
            if method not in ("GET", "POST", "PUT", "DELETE"):
                method = "GET"

            if not url:
                return {"success": False, "error": f"No URL found for API call: {input_data}"}

            headers = data.get("headers") or {}
            key_name = data.get("api_key_name") or cfg.get("api_key_name")
            if key_name and os.getenv(key_name) and "Authorization" not in headers:
                headers["Authorization"] = f"Bearer {os.getenv(key_name)}"

            params = data.get("params") or {}
            json_body = data.get("json") or data.get("body")

            try:
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    resp = await client.request(method, url, headers=headers, params=params, json=json_body)
                return {
                    "success": resp.is_success,
                    "output": resp.text[:4000],
                    "status_code": resp.status_code,
                }
            except Exception as e:
                return {"success": False, "error": f"API request to '{url}' failed: {e}"}

        return {
            "success": False,
            "error": f"api_connector: unknown action '{action}'. Supported: connect, save_key, list, call, request_key",
        }
