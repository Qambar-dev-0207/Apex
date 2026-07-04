import asyncio
import json
import os
from typing import List, Dict, Any
from google import genai
from src.core.models import KnowledgeArtifact
from src.core.agents import WebResearcher, FileResearcher, CodeAnalyst
from dotenv import load_dotenv

class KnowledgeSynthesizer:
    """
    Uses Gemini Flash to merge heterogeneous research data.
    """
    def __init__(self, model_name: str = "gemini-3.5-flash"):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.model_id = model_name

    async def synthesize(self, topic: str, data: List[Dict[str, Any]]) -> KnowledgeArtifact:
        if not self.client:
            return KnowledgeArtifact(
                topic=topic,
                summary="Client offline. Manual merge follows.",
                findings=data,
                sources=[d.get('source', 'unknown') for d in data],
                confidence_score=0.5
            )

        prompt = f"""
        Synthesize the following research data into a single Knowledge Artifact.
        TOPIC: {topic}
        DATA: {json.dumps(data, indent=2)}
        
        Output MUST be valid JSON matching the KnowledgeArtifact schema:
        {{
            "topic": "...",
            "summary": "High-level conclusion",
            "findings": [{{ "key": "val" }}],
            "sources": ["..."],
            "confidence_score": 0.0-1.0
        }}
        """
        
        try:
            res = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            return KnowledgeArtifact(**json.loads(res.text))
        except Exception as e:
            return KnowledgeArtifact(
                topic=topic,
                summary=f"Synthesis error: {e}",
                findings=data,
                sources=[d.get('source', 'unknown') for d in data],
                confidence_score=0.1
            )

class ResearchSwarm:
    """
    Orchestrates a parallel pool of research agents.
    """
    def __init__(self, workspace_root: str = "."):
        self.agents = [
            WebResearcher(),
            FileResearcher(workspace_root),
            CodeAnalyst(workspace_root)
        ]
        self.synthesizer = KnowledgeSynthesizer()

    async def run_swarm(self, query: str) -> KnowledgeArtifact:
        """
        Runs all agents in parallel and synthesizes the result.
        """
        raw_results = []
        
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(agent.research(query)) for agent in self.agents]
            
        raw_results = [t.result() for t in tasks]
        
        # Synthesize the results
        ska = await self.synthesizer.synthesize(query, raw_results)
        return ska
