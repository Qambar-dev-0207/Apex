import pytest
import sys
import os
import json
from unittest.mock import MagicMock, patch, AsyncMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.models import Skill, ExecutionPlan, TaskStep
from src.services.raphael import Raphael, GeniusMode
from src.services.learning import SkillManager, LearningManager
from src.core.skills_library import get_god_mode_skills


def test_skill_tier_promotions():
    """Verify that Skill models calculate and promote Tensura tiers appropriately."""
    plan = ExecutionPlan(
        task_plan=[TaskStep(id=1, action="test", description="step 1")],
        tools_required=[],
        requires_clarification=False,
        summary="Test plan"
    )
    skill = Skill(
        name="Test Fire Skill",
        description="Emits flame",
        query_pattern="cast fire",
        plan_template=plan,
        tier="Common",
        usage_count=1
    )
    assert skill.tier == "Common"

    # Increment to 5 uses -> Extra
    for _ in range(4):
        skill.reinforce()
    assert skill.usage_count == 5
    assert skill.tier == "Extra"
    assert len(skill.evolution_history) >= 1

    # Increment to 15 uses -> Unique
    for _ in range(10):
        skill.reinforce()
    assert skill.usage_count == 15
    assert skill.tier == "Unique"

    # Increment to 30 uses -> Ultimate
    for _ in range(15):
        skill.reinforce()
    assert skill.usage_count == 30
    assert skill.tier == "Ultimate"


def test_god_mode_skills_ultimate_raphael():
    """Verify built-in god mode skills have Raphael as the pinnacle Ultimate Skill."""
    skills = get_god_mode_skills()
    skill_names = {s.name: s for s in skills}
    
    assert "Raphael: Lord of Wisdom" in skill_names
    raphael_skill = skill_names["Raphael: Lord of Wisdom"]
    assert raphael_skill.tier == "Ultimate"
    assert raphael_skill.ultimate_name == "Raphael: Lord of Wisdom"
    assert raphael_skill.usage_count >= 30


def test_raphael_alias_compatibility():
    """Verify GeniusMode is a drop-in alias of Raphael."""
    assert GeniusMode is Raphael
    r = Raphael()
    g = GeniusMode()
    assert isinstance(g, Raphael)
    stub = r._stub("offline test")
    assert "cross_question" in stub
    assert "action" in stub
    assert "one_liner" in stub


@pytest.mark.asyncio
async def test_raphael_skill_evolution():
    """Verify Raphael can rewrite a failing skill into an evolved Unique/Ultimate skill."""
    plan = ExecutionPlan(
        task_plan=[TaskStep(id=1, action="flawed_action", description="step 1")],
        tools_required=[],
        requires_clarification=False,
        summary="Flawed plan"
    )
    skill = Skill(
        name="Buggy Query Skill",
        description="Fails on complex input",
        query_pattern="query buggy",
        plan_template=plan,
        tier="Common",
        usage_count=2
    )
    
    raphael = Raphael()
    evolved = await raphael.evolve_skill(skill, failure_context="Step 1 returned 500 error")
    
    assert evolved.tier in ("Unique", "Ultimate")
    assert len(evolved.evolution_history) > 0
    assert "Raphael Evolution" in evolved.evolution_history[-1]
