import asyncio
import os
import json
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from google import genai
from src.core.models import BriefingReport, ProjectManifest
from src.tools.workspace import WorkspaceManager
from src.core.telemetry import SpendTracker
from dotenv import load_dotenv

class DeadlineRadar:
    """
    Scans project manifests for at-risk deadlines.
    """
    def check_risks(self, project: ProjectManifest) -> List[str]:
        risks = []
        today = date.today()
        for dl in project.deadlines:
            try:
                target = datetime.strptime(dl['date'], '%Y-%m-%d').date()
                days_left = (target - today).days
                if days_left < 0:
                    risks.append(f"OVERDUE: '{dl['task']}' was due on {dl['date']}")
                elif days_left < 3:
                    risks.append(f"CRITICAL: '{dl['task']}' due in {days_left} days")
            except:
                pass
        return risks

class BriefingAgent:
    """
    Generates a proactive morning report.
    """
    def __init__(self, workspace: WorkspaceManager, spend: SpendTracker, forge=None):
        load_dotenv()
        self.workspace = workspace
        self.spend = spend
        self.forge = forge
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.radar = DeadlineRadar()

    async def generate_briefing(self) -> BriefingReport:
        today_str = date.today().isoformat()
        active_project = self.workspace.get_active()
        
        # 1. Gather raw context
        tasks = []
        risks = []
        if active_project:
            tasks = [t['task'] for t in active_project.todos if not t.get('done')]
            risks = self.radar.check_risks(active_project)
        
        daily_spend = self.spend.get_daily_spend()

        forge_digest = {}
        if self.forge:
            try:
                forge_digest = self.forge.briefing_digest()
            except Exception:
                pass

        # 2. Use Gemini to synthesize strategy
        strategy = "Rise and shine, Architect. The systems are humming, though your todo list is looking a bit neglected."
        if self.client:
            prompt = f"""
            IDENT: APEX // PROACTIVE BRIEFING PROTOCOL
            MODE: JARVIS // STRATEGIC ADVISOR

            Generate a concise, witty, and strategic daily briefing for the Architect.
            ACTIVE PROJECT: {active_project.name if active_project else 'None'}
            OPEN TASKS: {tasks[:5]}
            RISK ALERTS: {risks}
            DAILY SPEND: ${daily_spend:.4f}
            FORGE DIGEST: {forge_digest}

            Format: One paragraph of cinematic, cunning, and strategic advice. If the forge digest shows new applicable papers/proposals, surface them. Mention the spend if it's getting high. Crack a joke about the workload.
            """
            try:
                res = self.client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
                strategy = res.text.strip()
            except:
                pass

        return BriefingReport(
            date=today_str,
            high_priority_tasks=tasks[:3],
            risk_alerts=risks,
            suggested_strategy=strategy,
            spend_summary=f"Daily spend is at ${daily_spend:.4f}."
        )
