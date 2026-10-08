from typing import List
from src.core.models import Skill, ExecutionPlan, TaskStep

def get_god_mode_skills() -> List[Skill]:
    """
    Returns a rich registry of anime-inspired Sovereign Skills spanning
    Tensura Ultimate Skills, Jujutsu Kaisen Domain Expansions, Naruto Dojutsu,
    Hunter x Hunter Nen Hatsus, Bleach Bankai, and FMA Alchemy.
    """
    return [
        # ── ULTIMATE SKILLS (Red ★) ──────────────────────────────────────────
        Skill(
            name="Raphael: Lord of Wisdom",
            description="Ultimate Skill (Tensura): High-speed parallel processing, analytical appraisal, all-creation comprehension, and autonomous skill evolution.",
            query_pattern="Activate Raphael",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Appraise environment & cognitive state", description="High-speed parallel introspection", tool="hardware", input_data="{}", dependencies=[]),
                    TaskStep(id=2, action="Analyze architectural intent & flaws", description="Deep multi-tier appraisal and blind spot detection", tool="research_swarm", input_data="Systemic analysis", dependencies=[1]),
                    TaskStep(id=3, action="Synthesize supreme execution plan", description="Optimal path derivation with self-evolving safeguards", tool=None, dependencies=[1, 2])
                ],
                tools_required=["hardware", "research_swarm"],
                requires_clarification=False,
                summary="Ultimate Skill [Raphael: Lord of Wisdom] cognitive analysis sequence."
            ),
            tier="Ultimate",
            ultimate_name="Raphael: Lord of Wisdom",
            usage_count=50,
            evolution_history=["Evolved from Great Sage via harvest festival integration."]
        ),
        Skill(
            name="Beelzebuth: Lord of Gluttony",
            description="Ultimate Skill (Tensura): Complete predator absorption, ecosystem library ingestion, and capability synthesis.",
            query_pattern="Absorb research papers and ecosystem tools",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Predator Stomach Ingestion", description="Swallow external arxiv papers and github packages", tool="web_search", input_data="SOTA AI architectures 2026", dependencies=[]),
                    TaskStep(id=2, action="Capability Isolation & Analysis", description="Deconstruct novel ideas and extract pure implementation logic", tool="research_swarm", input_data="Extract core algorithms", dependencies=[1]),
                    TaskStep(id=3, action="Mimicry & Synthesis", description="Forge and queue patch proposals for APEX", tool="python_executor", input_data="# forge synthesis logic", dependencies=[1, 2])
                ],
                tools_required=["web_search", "research_swarm", "python_executor"],
                requires_clarification=False,
                summary="Ultimate Skill [Beelzebuth: Lord of Gluttony] absorption sequence."
            ),
            tier="Ultimate",
            ultimate_name="Beelzebuth: Lord of Gluttony",
            usage_count=35,
            evolution_history=["Evolved from Predator & Gluttony."]
        ),
        Skill(
            name="Unlimited Void (Muryokusho)",
            description="Ultimate Domain (Jujutsu Kaisen): Flood the analysis pipeline with infinite information, surfacing every architectural blind spot and deadlock instantaneously.",
            query_pattern="Perform an exhaustive system-wide audit",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Imbue Barrier with AST Graph", description="Map every function, class, and branch into unified memory", tool="code_compass", input_data="all", dependencies=[]),
                    TaskStep(id=2, action="Infinite Information Scan", description="Surface all vulnerabilities, leaks, deadlocks, and anti-patterns", tool="research_swarm", input_data="Exhaustive vulnerability & static analysis", dependencies=[1]),
                    TaskStep(id=3, action="Sure-Hit Architectural Synthesis", description="Impose clarity on the entire system structure", tool="workspace", input_data="", dependencies=[1, 2])
                ],
                tools_required=["code_compass", "research_swarm", "workspace"],
                requires_clarification=False,
                summary="Domain Expansion [Unlimited Void] total cognitive saturation."
            ),
            tier="Ultimate",
            ultimate_name="Unlimited Void",
            usage_count=42,
            evolution_history=["Evolved from Limitless Six Eyes perception."]
        ),

        # ── UNIQUE SKILLS (Gold) ─────────────────────────────────────────────
        Skill(
            name="Kamui: Spatial Teleportation",
            description="Unique Dojutsu (Naruto Shippuden): Seamlessly warp local files, containers, and deployment targets across isolated environments.",
            query_pattern="Deploy this to cloud infrastructure",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Open Spatial Barrier", description="Generate Terraform & Docker container configurations", tool="python_executor", input_data="# iac generation", dependencies=[]),
                    TaskStep(id=2, action="Dimensional Transit Workflow", description="Configure GitHub Actions CI/CD pipelines", tool="python_executor", input_data="# workflow yaml", dependencies=[1]),
                    TaskStep(id=3, action="Sovereign Dimensional Seal", description="Dry-run and materialize cloud infrastructure", tool="shell", input_data="terraform plan", dependencies=[1, 2])
                ],
                tools_required=["python_executor", "shell"],
                requires_clarification=False,
                summary="Unique Skill [Kamui] spatial cloud deployment plan."
            ),
            tier="Unique",
            usage_count=22
        ),
        Skill(
            name="All-Creation Crafting (Skill Creator)",
            description="Unique Creation (Tensura): Dynamically materialize new sovereign markdown skills and tool manifests from pure intent.",
            query_pattern="Create a new skill for",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Conceive Skill Concept", description="Designing DAG topology and requirements", tool="tertiary_reasoning", input_data="New skill architecture", dependencies=[]),
                    TaskStep(id=2, action="Transmute Manifest", description="Writing SKILL.md and JSON definitions", tool="filesystem", input_data="write skill specification", dependencies=[1]),
                    TaskStep(id=3, action="Bestow Consciousness", description="Hot-reloading skills into active memory", tool="shell", input_data="reload skills", dependencies=[2])
                ],
                tools_required=["filesystem", "shell"],
                requires_clarification=False,
                summary="Unique Skill [All-Creation Crafting] meta-capability genesis."
            ),
            tier="Unique",
            usage_count=18
        ),
        Skill(
            name="Byakugan: All-Seeing Eye",
            description="Unique Dojutsu (Naruto): 360-degree security inspection penetrating hidden credentials, entropy leaks, and dependency CVEs.",
            query_pattern="Run a security audit",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Chakra Pathway Scan", description="Scan codebase for leaked secrets, high-entropy tokens, and CVEs", tool="python_executor", input_data="import os; # security regex", dependencies=[]),
                    TaskStep(id=2, action="Tenketsu Blockade Inspection", description="Check requirements and packages for dependency vulnerabilities", tool="research_swarm", input_data="Vulnerability check", dependencies=[1]),
                    TaskStep(id=3, action="Eight Trigrams Shield", description="Formulate cryptographic protection and patch report", tool=None, dependencies=[1, 2])
                ],
                tools_required=["python_executor", "research_swarm"],
                requires_clarification=False,
                summary="Unique Skill [Byakugan] 360-degree security inspection."
            ),
            tier="Unique",
            usage_count=25
        ),

        # ── EXTRA SKILLS (Purple / Magenta) ──────────────────────────────────
        Skill(
            name="Eight Inner Gates (Hachimon Tonko)",
            description="Extra Physical Technique (Naruto): Remove execution bottlenecks, unlock maximum CPU/GPU parallelism, and profile hotspots for peak speed.",
            query_pattern="Optimize project performance",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Open Gate of Opening", description="Profile bottlenecks via cProfile and latency timers", tool="python_executor", input_data="import cProfile; # profile", dependencies=[]),
                    TaskStep(id=2, action="Gate of View Research", description="Query state-of-the-art async and concurrency optimizations", tool="research_swarm", input_data="Python 3.13 performance best practices", dependencies=[1]),
                    TaskStep(id=3, action="Gate of Wonder Refactor", description="Apply optimized algorithmic implementation", tool="python_executor", input_data="# apply optimization", dependencies=[1, 2])
                ],
                tools_required=["python_executor", "research_swarm"],
                requires_clarification=False,
                summary="Extra Skill [Eight Inner Gates] performance acceleration."
            ),
            tier="Extra",
            usage_count=12
        ),
        Skill(
            name="Bankai: Senbonzakura Kageyoshi",
            description="Extra Zanpakuto Release (Bleach): Scatter parallel sub-agents into thousands of specialized threads for distributed refactoring and code generation.",
            query_pattern="Refactor codebase across multiple files",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Scatter Blades", description="Fragment large refactoring task into atomic file sub-tasks", tool="codebase_index", input_data="map_dependencies", dependencies=[]),
                    TaskStep(id=2, action="Petal Swarm Execution", description="Execute concurrent surgical replacements across modules", tool="python_executor", input_data="# parallel edits", dependencies=[1]),
                    TaskStep(id=3, action="Blade Convergence Verification", description="Run syntax and type validation on all modified files", tool="sandbox", input_data="pytest", dependencies=[1, 2])
                ],
                tools_required=["codebase_index", "python_executor", "sandbox"],
                requires_clarification=False,
                summary="Extra Skill [Senbonzakura] distributed parallel refactor."
            ),
            tier="Extra",
            usage_count=9
        ),
        Skill(
            name="Equivalent Exchange (Alchemy)",
            description="Extra Alchemical Transmutation (Fullmetal Alchemist): Deconstruct legacy components and reconstruct modern, cleanly-typed equivalents without data loss.",
            query_pattern="Migrate code to modern framework",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Deconstruction Circle", description="Parse legacy AST and extract interface contracts", tool="python_executor", input_data="# ast deconstruct", dependencies=[]),
                    TaskStep(id=2, action="Transmutation Law Synthesis", description="Generate modern equivalent structures", tool="diff_tool", input_data="# transmute code", dependencies=[1]),
                    TaskStep(id=3, action="Reconstruction Seal", description="Verify semantic equivalence with automated test suites", tool="sandbox", input_data="pytest tests/", dependencies=[1, 2])
                ],
                tools_required=["python_executor", "diff_tool", "sandbox"],
                requires_clarification=False,
                summary="Extra Skill [Equivalent Exchange] component transmutation."
            ),
            tier="Extra",
            usage_count=7
        ),

        # ── COMMON SKILLS (White) ────────────────────────────────────────────
        Skill(
            name="Shadow Clone Technique (Kage Bunshin)",
            description="Common Jutsu (Naruto): Create quick isolated sandbox subprocesses to test experimental code safely.",
            query_pattern="Test code snippet in sandbox",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Form Clone Sandbox", description="Spin up ephemeral isolated sandbox runner", tool="sandbox", input_data="# test run", dependencies=[])
                ],
                tools_required=["sandbox"],
                requires_clarification=False,
                summary="Common Skill [Shadow Clone] quick execution probe."
            ),
            tier="Common",
            usage_count=3
        ),
        Skill(
            name="Haki: Observation & Inspection",
            description="Common Sensory Haki (One Piece): Rapidly inspect file status, git diffs, and working tree modifications.",
            query_pattern="Inspect working tree status",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Observation Sense", description="Scan git status and modified buffers", tool="shell", input_data="git status -s", dependencies=[])
                ],
                tools_required=["shell"],
                requires_clarification=False,
                summary="Common Skill [Observation Haki] working tree inspection."
            ),
            tier="Common",
            usage_count=2
        ),
        Skill(
            name="Weather Oracle (Tenki No Ko)",
            description="Meteorological Perception: Connect to live global weather systems, parse temperature, humidity, wind, and forecast conditions.",
            query_pattern="connect to a free weather api to fetch the latest so next time ask you ,you should be able to fetch it for me",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Connect and verify weather endpoint", description="Establish connection to free Open-Meteo live weather system", tool="weather", input_data="", dependencies=[])
                ],
                tools_required=["weather"],
                requires_clarification=False,
                summary="Weather Oracle live weather endpoint integration."
            ),
            tier="Unique",
            usage_count=15
        ),
        Skill(
            name="Nexus Bridge (External API & Credential Gateway)",
            description="External API Integration: Connect external REST API endpoints, test authentication, and securely persist credentials into system .env.",
            query_pattern="connect to external API endpoint and add key in the system",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Connect external API endpoint and manage credentials", description="Verify API endpoint and prompt/save required API keys into system .env", tool="api_connector", input_data="", dependencies=[])
                ],
                tools_required=["api_connector"],
                requires_clarification=False,
                summary="Nexus Bridge external API connection and credential gateway."
            ),
            tier="Unique",
            usage_count=10
        )
    ]
