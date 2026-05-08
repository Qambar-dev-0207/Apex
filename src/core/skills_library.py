from typing import List
from src.core.models import Skill, ExecutionPlan, TaskStep

def get_god_mode_skills() -> List[Skill]:
    """
    Returns a list of high-tier pre-defined skills.
    """
    return [
        Skill(
            name="Apex Security Auditor",
            description="Deep scan for vulnerabilities, secrets, and insecure patterns.",
            query_pattern="Run a security audit",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Scan codebase for secrets", description="Using regex and entropy checks", tool="python_executor", input_data="import os; # scan logic", dependencies=[]),
                    TaskStep(id=2, action="Analyze dependency graph", description="Checking requirements.txt for CVEs", tool="research_swarm", input_data="Vulnerability check for project deps", dependencies=[]),
                    TaskStep(id=3, action="Summarize security posture", description="Risk assessment", tool=None, dependencies=[1, 2])
                ],
                tools_required=["python_executor", "research_swarm"],
                requires_clarification=False,
                summary="Full stack security audit initialized."
            )
        ),
        Skill(
            name="System Performance Optimizer",
            description="Profile code and propose optimization paths.",
            query_pattern="Optimize project performance",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Identify bottlenecks", description="Profiling local scripts", tool="python_executor", input_data="import cProfile; # profile logic", dependencies=[]),
                    TaskStep(id=2, action="Research SOTA optimizations", description="Looking for 2026 performance patterns", tool="research_swarm", input_data="Python 3.13 performance best practices", dependencies=[]),
                    TaskStep(id=3, action="Apply refactor", description="Refactor hotspot", tool="python_executor", input_data="# refactor logic", dependencies=[1, 2])
                ],
                tools_required=["python_executor", "research_swarm"],
                requires_clarification=False,
                summary="End-to-end performance optimization schematic."
            )
        ),
        Skill(
            name="Cloud Infrastructure Architect",
            description="Generate IaC and deployment pipelines.",
            query_pattern="Deploy this to the cloud",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Generate Terraform/IaC", description="Infrastructure as Code", tool="python_executor", input_data="# terraform gen logic", dependencies=[]),
                    TaskStep(id=2, action="Create GitHub Actions workflow", description="CI/CD config", tool="python_executor", input_data="# yaml gen logic", dependencies=[]),
                    TaskStep(id=3, action="Validate configuration", description="Dry-run check", tool="python_executor", input_data="# validate logic", dependencies=[1, 2])
                ],
                tools_required=["python_executor"],
                requires_clarification=False,
                summary="Cloud sovereignty deployment plan."
            )
        ),
        Skill(
            name="Apex Skill Creator",
            description="Dynamically generate new markdown skills for APEX.",
            query_pattern="Create a new skill for",
            plan_template=ExecutionPlan(
                task_plan=[
                    TaskStep(id=1, action="Brainstorm skill logic", description="Designing the DAG for the new skill", tool="tertiary_reasoning", input_data="New skill design", dependencies=[]),
                    TaskStep(id=2, action="Generate SKILL.md", description="Writing the markdown manifest", tool="filesystem", input_data="write skill md", dependencies=[1]),
                    TaskStep(id=3, action="Reload system skills", description="Activating the new capability", tool="shell", input_data="reload skills", dependencies=[2])
                ],
                tools_required=["filesystem", "shell"],
                requires_clarification=False,
                summary="Meta-skill generation sequence."
            )
        )
    ]
