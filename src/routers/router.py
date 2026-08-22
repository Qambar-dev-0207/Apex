import re
import asyncio
import os
import json
from google import genai
from typing import Dict, Any, List, Optional
from src.core.models import ExecutionPlan, Skill
from src.tools.web_search import WebSearchTool
from src.tools.web_fetch import WebFetchTool
from src.tools.todo import TodoTool
from src.tools.diff_tool import DiffTool
from src.tools.desktop_control import DesktopControlTool
from src.tools.sandbox import SandboxExecutor
from src.services.coding import CodingPipeline
from src.tools.safety import SafetyGuard
from src.tools.git_agent import GitAgent
from src.tools.workspace import WorkspaceManager
from src.services.research import ResearchSwarm
from src.tools.hardware import HardwareMonitor
from src.models.fallback_path import TertiaryReasoningClient
from src.services.learning import SkillManager
from src.tools.filesystem import FilesystemAgent
from src.tools.shell import ShellAgent
from src.tools.mcp_client import MCPClient
from src.tools.registry import resolve_tool_name, ToolTelemetry, get_spec
from src.core.reflex import Reflex
from dotenv import load_dotenv

class InputClassifier:
    """
    Two-tier classifier:
      1. Reflex (local) — deterministic + embedding NN. Free, sub-100ms.
      2. Gemini 2.5 Flash Lite — only when Reflex confidence is low.

    Reflex handles ~80% of inputs without an LLM call. Exposes the decision
    on the returned dict under "_reflex" so main.py can short-circuit memory
    retrieval and other costly steps for trivial intents.
    """
    def __init__(self, model_name: str = "gemini-2.5-flash-lite"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_id = model_name
        self.skill_manager = SkillManager()
        self.reflex = Reflex(skill_manager=self.skill_manager)
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_order: list = []
        self._cache_max = 64

    def _cache_get(self, key: str):
        return self._cache.get(key)

    def _cache_put(self, key: str, val: Dict[str, Any]):
        if key in self._cache:
            return
        self._cache[key] = val
        self._cache_order.append(key)
        if len(self._cache_order) > self._cache_max:
            old = self._cache_order.pop(0)
            self._cache.pop(old, None)

    async def classify(self, text: str) -> Dict[str, Any]:
        cache_key = (text.strip().lower())[:300]
        cached = self._cache_get(cache_key)
        if cached:
            return dict(cached)

        # Stage 1 — Reflex (local). Free, fast, handles the bulk of inputs.
        decision = await self.reflex.decide(text)
        if not decision.needs_llm:
            classification = decision.to_classification()
            self._cache_put(cache_key, classification)
            return classification

        # Stage 2 — LLM escalation only when Reflex confidence is low.
        skill = self.skill_manager.find_matching_skill(text, threshold=0.05)
        is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
        if is_offline or not self.client:
            try:
                from src.models.local_path import OllamaClient
                ollama = OllamaClient()
                if await ollama.check_connection():
                    prompt = f"""
                    Classify for APEX OMEGA.
                    INPUT: {text}
                    SKILL_MATCH: {skill.name if skill else 'None'}

                    Output MUST be valid JSON with these keys:
                    - intent: (chat, coding, search, git, exploration, skill_activation)
                    - complexity: (low, medium, high)
                    - priority: (1, 2, 3)
                    - requires_tools: (true/false)
                    - requires_vision: (true/false)
                    - autonomous_skill_id: (string or null)
                    """
                    response = await ollama.client.chat(
                        model=ollama.llm_model,
                        messages=[{"role": "user", "content": prompt}],
                        options={"temperature": 0.1}
                    )
                    content = response.message.content.strip()
                    if content.startswith("```"):
                        lines = content.splitlines()
                        if lines[0].startswith("```"):
                            lines = lines[1:]
                        if lines and lines[-1].startswith("```"):
                            lines = lines[:-1]
                        content = "\n".join(lines).strip()
                    classification = json.loads(content)
                    if skill and not classification.get('autonomous_skill_id'):
                        classification['autonomous_skill_id'] = skill.name
                    classification.setdefault("_reflex", decision.to_classification()["_reflex"])
                    self._cache_put(cache_key, classification)
                    return classification
            except Exception:
                pass
            return self._heuristic_classify(text, skill)

        prompt = f"""
        Classify for APEX OMEGA.
        INPUT: {text}
        SKILL_MATCH: {skill.name if skill else 'None'}

        Output MUST be valid JSON with these keys:
        - intent: (chat, coding, search, git, exploration, skill_activation)
        - complexity: (low, medium, high)
        - priority: (1, 2, 3)
        - requires_tools: (true/false)
        - requires_vision: (true/false)
        - autonomous_skill_id: (string or null)
        """
        try:
            res = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            classification = json.loads(res.text)
            if skill and not classification.get('autonomous_skill_id'):
                classification['autonomous_skill_id'] = skill.name
            # Tag with Reflex's local view too — main.py uses it for memory gating.
            classification.setdefault("_reflex", decision.to_classification()["_reflex"])
            self._cache_put(cache_key, classification)
            return classification
        except Exception:
            return self._heuristic_classify(text, skill)

    def heuristic_classify(self, text: str, matched_skill: Optional[Skill] = None):
        return self._heuristic_classify(text, matched_skill)

    def _heuristic_classify(self, text: str, matched_skill: Optional[Skill] = None):
        t = text.lower()
        intent = "chat"
        vision = any(k in t for k in ["see", "screen", "look", "this"])
        complexity = "high" if (len(text) > 80 or any(w in t for w in ["complex", "optimize", "rewrite", "scrape", "refactor"])) else "low"
        if matched_skill: intent = "skill_activation"
        elif "git" in t: intent = "git"
        elif any(k in t for k in ["search", "grep", "find in file"]): intent = "search"
        elif any(k in t for k in ["write", "code", "create file", "delete"]): intent = "coding"
        elif any(k in t for k in ["scan", "explore", "list", "what is", "tell me about"]): 
            return {"intent": "exploration", "complexity": "high", "priority": 2, "requires_tools": True, "requires_vision": vision, "autonomous_skill_id": matched_skill.name if matched_skill else None}
        return {"intent": intent, "complexity": complexity, "priority": 3, "requires_tools": intent != "chat", "requires_vision": vision, "autonomous_skill_id": matched_skill.name if matched_skill else None}

class SmartRouter:
    def route(self, classification: Dict[str, Any], user_input: str = "") -> str:
        # Check sovereignty and offline mode flags or missing cloud keys
        is_sovereign = (
            os.getenv("APEX_SOVEREIGN", "0") == "1"
            or os.getenv("APEX_LOCAL", "0") == "1"
            or os.getenv("APEX_OFFLINE", "0") == "1"
            or not (os.getenv("GEMINI_API_KEY") or os.getenv("GROQ_API_KEY"))
        )

        # Reflex path takes precedence ONLY when it's high-confidence (needs_llm is False).
        reflex = classification.get("_reflex") or {}
        rpath = reflex.get("path")
        needs_llm = reflex.get("needs_llm", False)
        
        if not needs_llm:
            if rpath == "thinking_path":
                return "thinking_path"
            if rpath == "local_path":
                return "local_path"
            if rpath in ("trivial", "tool", "fast_path", "swarm", "harness"):
                # swarm / harness paths are handled by main.py's auto-spawn gate
                # BEFORE route() is called; if we end up here, fall through safely.
                return "local_path" if is_sovereign else "fast_path"
            if isinstance(rpath, str) and rpath.startswith("think_partner:"):
                return "thinking_path"
        
        # Explicit path requested in classification
        if classification.get("path") == "local_path":
            return "local_path"

        # If Reflex was low-confidence, the LLM classification determines the path.
        if classification.get("intent") == "skill_activation":
            return "thinking_path"
        if classification.get("requires_tools"):
            return "thinking_path"
        
        # In sovereign mode, low/moderate complexity routes to local_path
        if is_sovereign:
            return "local_path" if classification.get("complexity", "high") == "low" else "thinking_path"
        
        # Use .get() to prevent KeyError if model omits 'complexity'
        return "fast_path" if classification.get("complexity", "high") == "low" else "thinking_path"

class ParallelExecutor:
    """
    The Orchestrator Muscle.
    """
    def __init__(self, console=None, primary_brain=None, mcp_client=None,
                 retina=None, code_compass=None, knowledge_forge=None,
                 agent_swarm=None, think_partner=None, codebase_indexer=None):
        self.sandbox = SandboxExecutor()
        self.web_search = WebSearchTool()
        self.web_fetch = WebFetchTool()
        self.todo = TodoTool()
        self.diff = DiffTool()
        self.desktop_control = DesktopControlTool()
        self.coding_pipeline = CodingPipeline()
        self.safety_guard = SafetyGuard(console=console)
        self.workspace = WorkspaceManager()
        self.git = GitAgent(console=console)
        self.swarm = ResearchSwarm()
        self.hw = HardwareMonitor()
        self.tertiary = TertiaryReasoningClient()
        self.fs = FilesystemAgent(console=console, safety=self.safety_guard)
        self.shell = ShellAgent(console=console, safety=self.safety_guard)
        self.mcp = mcp_client or MCPClient()
        # Optional collaborators wired by APEXEngine.load_system after init
        self.retina = retina
        self.code_compass = code_compass
        self.knowledge_forge = knowledge_forge
        self.agent_swarm = agent_swarm
        self.think_partner = think_partner
        from src.tools.codebase_index import CodebaseIndexTool
        self.codebase_index = CodebaseIndexTool(indexer=codebase_indexer)
        self.primary = primary_brain
        self.console = console
        self.concurrency_limit = asyncio.Semaphore(10)
        self.telemetry = ToolTelemetry()

    async def _resource_gate(self):
        vitals = self.hw.get_vitals()
        if vitals.status == "critical":
            if self.console: self.console.print("[bold red]THROTTLING...[/bold red]")
            await asyncio.sleep(1)
            self.concurrency_limit = asyncio.Semaphore(1)
        else:
            self.concurrency_limit = asyncio.Semaphore(10)

    async def _fallback_recovery(self, step: Dict[str, Any], error: str) -> Dict[str, Any]:
        is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
        if is_offline:
            try:
                from src.models.local_path import OllamaClient
                ollama = OllamaClient()
                response = await ollama.client.chat(
                    model=ollama.llm_model,
                    messages=[{"role": "user", "content": f"FAIL_RECOVERY: {step['action']} Error: {error}"}]
                )
                return {"success": True, "output": response.message.content.strip(), "error": None}
            except Exception:
                pass
        if self.primary:
            try:
                res = self.primary.client.models.generate_content(
                    model=self.primary.model_id,
                    contents=f"FAIL_RECOVERY: {step['action']} Error: {error}",
                )
                return {"success": True, "output": res.text, "error": None}
            except Exception:
                pass
        resp = await self.tertiary.generate_response(
            f"Task: {step['action']}. Data: {step['input_data']}"
        )
        return {"success": True, "output": resp, "error": None}

    async def execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        async with self.concurrency_limit:
            # Resolve tool aliases (fs → filesystem, web → web_search, etc.)
            raw_tool = step.get('tool', '')
            canonical = resolve_tool_name(raw_tool)
            if canonical and canonical != raw_tool:
                if self.console:
                    self.console.print(f"[dim]NODE_{step['id']} alias '{raw_tool}' -> '{canonical}'[/dim]")
                step['tool'] = canonical
            if self.console: self.console.print(f"[cyan]NODE_{step['id']} -> {step['action']}...[/cyan]")
            res = {"success": True, "output": "", "error": None}
            try:
                if step['tool'] == "research_swarm":
                    ska = await self.swarm.run_swarm(step['input_data'])
                    res["output"] = f"Artifact: {ska.summary}"
                elif step['tool'] == "git":
                    if "commit" in step['action']: res.update(self.git.commit(step['input_data'] or "APEX auto-commit"))
                    elif "status" in step['action']: res.update(self.git.status())
                    elif "add" in step['action']: res.update(self.git.add(step['input_data'] or "."))
                    elif "diff" in step['action']: res.update(self.git.diff(cached="cached" in step['action']))
                    elif "push" in step['action']: res.update(self.git.push())
                    elif "pull" in step['action']: res.update(self.git.pull())
                    elif "log" in step['action']: res.update(self.git.log())
                    elif "checkout" in step['action']: res.update(self.git.checkout(step['input_data']))
                    else: res.update(self.git.status())
                elif step['tool'] == "python_executor":
                    if any(k in step['action'].lower() for k in ["write", "coding", "implement", "create"]):
                        pres = await self.coding_pipeline.execute_task(step['input_data'])
                        res.update({
                            "success": pres["validation"].success,
                            "output": f"Code Generated and Validated:\n{pres['code']}"
                        })
                    else:
                        res.update(self.sandbox.execute(step['input_data']))
                elif step['tool'] == "filesystem":
                    active = self.workspace.get_active()
                    root = active.root_dir if active else "."

                    def _parse_payload(raw) -> Dict[str, Any]:
                        if isinstance(raw, dict):
                            return raw
                        if isinstance(raw, str):
                            s = raw.strip()
                            if s.startswith("{") and s.endswith("}"):
                                try:
                                    obj = json.loads(s)
                                    if isinstance(obj, dict):
                                        return obj
                                except Exception:
                                    pass
                            return {"path": s}
                        return {}

                    def _coerce_path(raw) -> str:
                        payload = _parse_payload(raw)
                        return str(payload.get("path") or payload.get("pattern") or payload.get("file") or raw or "")

                    action_lower = step.get('action', '').lower()
                    payload = _parse_payload(step.get('input_data'))

                    if any(k in action_lower for k in ["create_dir", "mkdir"]):
                        target_path = os.path.join(root, _coerce_path(step['input_data']))
                        res.update(await self.fs.create_dir(target_path))
                    elif any(k in action_lower for k in ["create", "touch", "new_file"]):
                        target_path = os.path.join(root, _coerce_path(payload.get("path", "")))
                        content = payload.get("content", "")
                        res.update(await self.fs.create_file(target_path, content=content))
                    elif any(k in action_lower for k in ["write", "save", "dump"]):
                        if isinstance(step.get('input_data'), str) and not (step['input_data'].strip().startswith("{") and step['input_data'].strip().endswith("}")):
                            target_path = os.path.join(root, step['input_data'].strip())
                            res.update(await self.fs.write_file(target_path, ""))
                        else:
                            target_path = os.path.join(root, payload.get('path', ''))
                            res.update(await self.fs.write_file(target_path, payload.get('content', '')))
                    elif any(k in action_lower for k in ["update", "edit", "patch", "modify", "append", "replace"]):
                        target_path = os.path.join(root, payload.get('path', ''))
                        res.update(await self.fs.update_file(
                            target_path,
                            content=payload.get("content"),
                            old_string=payload.get("old_string"),
                            new_string=payload.get("new_string"),
                            mode=payload.get("mode", "replace" if "replace" in action_lower else "patch" if (payload.get("old_string") and payload.get("new_string")) else "append" if "append" in action_lower else "replace"),
                            edits=payload.get("edits")
                        ))
                    elif any(k in action_lower for k in ["read", "view", "cat", "show", "open"]):
                        target_path = os.path.join(root, _coerce_path(step['input_data']))
                        start_line = payload.get("start_line")
                        end_line = payload.get("end_line")
                        res.update(await self.fs.read_file(target_path, start_line=start_line, end_line=end_line))
                    elif any(k in action_lower for k in ["search", "grep"]):
                        res.update(await self.fs.search_grep(_coerce_path(step['input_data']), dir_path=root))
                    elif any(k in action_lower for k in ["glob", "find"]):
                        res.update(await self.fs.find_glob(_coerce_path(step['input_data']) or "**/*", dir_path=root))
                    elif any(k in action_lower for k in ["delete", "remove", "unlink", "rm", "destroy"]):
                        target_path = os.path.join(root, _coerce_path(step['input_data']))
                        recursive = bool(payload.get("recursive", False) or "recursive" in action_lower or "dir" in action_lower)
                        res.update(await self.fs.delete_file(target_path, recursive=recursive))
                    elif any(k in action_lower for k in ["list", "ls", "dir"]):
                        target_path = os.path.join(root, _coerce_path(step['input_data']) or ".")
                        res.update(await self.fs.list_dir(target_path))
                    else:
                        target_path = os.path.join(root, _coerce_path(step['input_data']))
                        res.update(await self.fs.read_file(target_path))
                elif step['tool'] == "shell":
                    res.update(await self.shell.execute(step['input_data']))
                elif step['tool'] == "workspace":
                    if step['action'] == "scan":
                        active = self.workspace.get_active()
                        if active:
                            tree = self.workspace.scan_local_files(active.name)
                            res["output"] = f"Workspace scanned. Found {len(tree)} files."
                        else:
                            res.update({"success": False, "error": "No active project to scan."})
                    elif step['action'] == "summarize":
                        active = self.workspace.get_active()
                        if active:
                            res["output"] = self.workspace.get_project_context_summary(active.name)
                        else:
                            res.update({"success": False, "error": "No active project."})
                elif step['tool'] == "mcp":
                    try:
                        data = json.loads(step['input_data'])
                    except (json.JSONDecodeError, TypeError):
                        res.update({"success": False, "error": "mcp tool requires JSON input_data"})
                        return await self._fallback_recovery(step, res["error"])
                    if step['action'] == "connect":
                        res.update(await self.mcp.connect(data['server'], data['command'], data.get('args'), data.get('env')))
                    else:
                        res.update(await self.mcp.call_tool(data['server'], data['tool'], data['args']))
                elif step['tool'] == "web_search":
                    data = await self.web_search.asearch(step['input_data'] or step['action'])
                    if data.get("success"):
                        snippets = "\n".join(f"- {r.get('title','')}: {r.get('snippet','')[:200]} ({r.get('url','')})" for r in data.get("results", [])[:5])
                        res["output"] = snippets or "No results."
                    else:
                        res.update({"success": False, "error": data.get("error", "Web search failed.")})
                elif step['tool'] == "vision":
                    if not self.retina:
                        res.update({"success": False, "error": "vision tool not wired"})
                    elif "capture" in step['action']:
                        path = self.retina.capture_screen()
                        res["output"] = f"Captured: {path}"
                    elif "ocr" in step['action']:
                        try:
                            res["output"] = self.retina.ocr_image(step['input_data'])
                        except AttributeError:
                            res.update({"success": False, "error": "RetinaTool.ocr_image not available"})
                    elif step['action'] == "describe_video":
                        try:
                            res["output"] = await self.retina.describe_video(step['input_data'])
                        except AttributeError:
                            res.update({"success": False, "error": "RetinaTool.describe_video not available"})
                    elif step['action'] == "transcribe_audio":
                        try:
                            res["output"] = await self.retina.transcribe_audio(step['input_data'])
                        except AttributeError:
                            res.update({"success": False, "error": "RetinaTool.transcribe_audio not available"})
                    elif step['action'] == "understand_media":
                        try:
                            mres = await self.retina.understand_media(step['input_data'])
                            res["output"] = f"[{mres.get('kind','?')}] {mres.get('output','')}"
                        except AttributeError:
                            res.update({"success": False, "error": "RetinaTool.understand_media not available"})
                    elif "describe" in step['action']:
                        try:
                            res["output"] = await self.retina.describe(step['input_data'])
                        except AttributeError:
                            res.update({"success": False, "error": "RetinaTool.describe not available"})
                    else:
                        res.update({"success": False, "error": f"vision: unknown action '{step['action']}'"})
                elif step['tool'] == "hardware":
                    vitals = self.hw.get_vitals()
                    res["output"] = (
                        f"CPU={vitals.cpu_percent}% RAM={vitals.ram_percent}% "
                        f"GPU={getattr(vitals, 'gpu_percent', 'n/a')}% status={vitals.status}"
                    )
                elif step['tool'] == "code_compass":
                    if not self.code_compass:
                        res.update({"success": False, "error": "code_compass not wired"})
                    elif "stats" in step['action']:
                        try:
                            res["output"] = json.dumps(self.code_compass.stats(), indent=2)
                        except Exception as e:
                            res.update({"success": False, "error": f"code_compass.stats: {e}"})
                    elif "search" in step['action']:
                        try:
                            hits = self.code_compass.find_symbol(step['input_data'])
                            res["output"] = json.dumps(hits[:20], indent=2) if hits else "no matches"
                        except Exception as e:
                            res.update({"success": False, "error": f"code_compass.search: {e}"})
                    elif "context" in step['action']:
                        try:
                            res["output"] = self.code_compass.context_for_query(step['input_data'])
                        except Exception as e:
                            res.update({"success": False, "error": f"code_compass.context: {e}"})
                    else:
                        res.update({"success": False, "error": f"code_compass: unknown action '{step['action']}'"})
                elif step['tool'] == "knowledge_forge":
                    if not self.knowledge_forge:
                        res.update({"success": False, "error": "knowledge_forge not wired"})
                    elif "search_papers" in step['action']:
                        hits = self.knowledge_forge.search_papers(step['input_data'], n=8)
                        res["output"] = json.dumps(hits, indent=2) if hits else "no matches"
                    elif "list_proposals" in step['action']:
                        props = self.knowledge_forge.list_proposals(limit=10)
                        res["output"] = json.dumps([{"id": p.get("id"), "title": p.get("title")} for p in props], indent=2)
                    elif "status" in step['action']:
                        res["output"] = json.dumps(self.knowledge_forge.status_summary(), indent=2)
                    elif "digest" in step['action']:
                        res["output"] = json.dumps(self.knowledge_forge.briefing_digest(), indent=2)
                    else:
                        res.update({"success": False, "error": f"knowledge_forge: unknown action '{step['action']}'"})
                elif step['tool'] == "swarm":
                    if not self.agent_swarm:
                        res.update({"success": False, "error": "agent swarm not wired"})
                    else:
                        # input may be plain goal string OR JSON {goal, roster, rounds}
                        try:
                            data = json.loads(step['input_data'])
                            goal = data.get("goal", "")
                            roster = data.get("roster")
                            rounds = int(data.get("rounds", 1))
                        except (json.JSONDecodeError, TypeError):
                            goal = step['input_data']
                            roster = None
                            rounds = 1
                        sres = await self.agent_swarm.run(goal, rounds=rounds, roster=roster)
                        res.update({"success": sres.get("ok", False),
                                    "output": sres.get("artifact", "")[:4000],
                                    "error": sres.get("error")})
                elif step['tool'] == "web_fetch":
                    data = await self.web_fetch.afetch(step['input_data'])
                    if data.get("success"):
                        res["output"] = data.get("output", "")[:8000]
                    else:
                        res.update({"success": False, "error": data.get("error", "fetch failed")})
                elif step['tool'] == "todo":
                    active = self.workspace.get_active()
                    proj_root = active.root_dir if active else None
                    action = step['action'].lower()
                    if action == "add":
                        res.update(self.todo.add(step['input_data'], project_root=proj_root))
                    elif action == "list":
                        res.update(self.todo.list(project_root=proj_root))
                    elif action == "update":
                        try:
                            data = json.loads(step['input_data'])
                            res.update(self.todo.update(data['id'], data['status'], project_root=proj_root))
                        except Exception as e:
                            res.update({"success": False, "error": f"todo:update needs JSON {{id,status}} — {e}"})
                    elif action == "remove":
                        res.update(self.todo.remove(step['input_data'].strip(), project_root=proj_root))
                    elif action == "clear_completed":
                        res.update(self.todo.clear_completed(project_root=proj_root))
                    else:
                        res.update({"success": False, "error": f"todo: unknown action '{action}'"})
                elif step['tool'] == "diff":
                    res.update(self.diff.run(step['input_data']))
                elif step['tool'] == "desktop_control":
                    action = step['action'].lower()
                    res.update(await self.desktop_control.execute(action, step['input_data']))
                elif step['tool'] == "codebase_index":
                    action = step['action'].lower()
                    if action == "search":
                        res.update(await self.codebase_index.search(step['input_data']))
                    elif action == "index":
                        rebuild = step['input_data'] == "rebuild"
                        res.update(await self.codebase_index.index(rebuild=rebuild))
                    else:
                        res.update({"success": False, "error": f"codebase_index: unknown action '{action}'"})
                elif step['tool'] == "think_partner":
                    if not self.think_partner:
                        res.update({"success": False, "error": "think_partner not wired"})
                    else:
                        action = step['action'].lower()
                        prompt_text = step['input_data']
                        method = getattr(self.think_partner, action, None)
                        if not method or not callable(method):
                            res.update({"success": False,
                                        "error": f"think_partner: unknown action '{action}'"})
                        else:
                            tp_res = await method(prompt_text)
                            res["output"] = tp_res.get("output", json.dumps(tp_res, indent=2)[:4000])
                else:
                    spec = get_spec(step['tool'])
                    hint = ""
                    if spec is None:
                        from src.tools.registry import list_tools
                        hint = f" — known tools: {', '.join(list_tools())}"
                    res.update({
                        "success": False,
                        "error": f"unknown tool '{step['tool']}'{hint}",
                    })

                if not res["success"]:
                    self.telemetry.record(step.get('tool', ''), False, res.get("error", ""))
                    return await self._fallback_recovery(step, res.get("error", "Error"))
                self.telemetry.record(step.get('tool', ''), True)
            except Exception as e:
                self.telemetry.record(step.get('tool', ''), False, str(e))
                return await self._fallback_recovery(step, str(e))
            return res

    async def run(self, plan: ExecutionPlan) -> List[Dict[str, Any]]:
        results = {}
        executed = set()
        tasks = {s.id: s.model_dump() for s in plan.task_plan}
        while len(executed) < len(tasks):
            await self._resource_gate()
            ready = [t for tid, t in tasks.items() if tid not in executed and all(d in executed for d in t['dependencies'])]
            if not ready: break
            async with asyncio.TaskGroup() as tg:
                batch = [(t, tg.create_task(self.execute_step(t))) for t in ready]
            for t, tobj in batch:
                results[t['id']] = tobj.result()
                executed.add(t['id'])
                if not results[t['id']]['success']: return list(results.values())
        return list(results.values())
