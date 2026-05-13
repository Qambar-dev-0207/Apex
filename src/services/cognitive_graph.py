import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional
from google import genai
from src.core.models import KnowledgeMap, KnowledgeNode, KnowledgeEdge
from src.services.memory import MemoryManager
from src.tools.workspace import WorkspaceManager
from dotenv import load_dotenv

class KnowledgeVisualizer:
    """
    Layer 10: Relational Cognitive Graph & Visualization.
    Maps interactions into a semantic graph for better context pruning.
    """
    def __init__(self, memory_manager: MemoryManager, workspace: WorkspaceManager):
        load_dotenv()
        self.memory = memory_manager
        self.workspace = workspace
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None
        self.current_map = KnowledgeMap()
        self._load_map()

    def _get_map_path(self):
        active = self.workspace.get_active()
        if active:
            return os.path.join(active.root_dir, ".apex", "knowledge_map.json")
        return "data/knowledge_map.json"

    def _load_map(self):
        map_path = self._get_map_path()
        if os.path.exists(map_path):
            try:
                with open(map_path, "r") as f:
                    self.current_map = KnowledgeMap.model_validate_json(f.read())
            except:
                self.current_map = KnowledgeMap()
        else:
            self.current_map = KnowledgeMap()

    def _save_map(self):
        map_path = self._get_map_path()
        os.makedirs(os.path.dirname(map_path), exist_ok=True)
        with open(map_path, "w") as f:
            f.write(self.current_map.model_dump_json(indent=2))

    async def extract_knowledge(self, user_input: str, assistant_output: str):
        """
        Uses Gemini to identify new entities and relations.
        """
        self._load_map() # Ensure we have the latest project-local map
        if not self.client: return

        prompt = f"""
        Analyze this interaction and extract semantic nodes and edges for a knowledge graph.
        
        USER: {user_input}
        AI: {assistant_output}
        
        CURRENT NODES: {[n.label for n in self.current_map.nodes]}
        
        Output JSON:
        {{
            "new_nodes": [{{ "id": "id", "label": "name", "type": "type", "summary": "short" }}],
            "new_edges": [{{ "source": "id1", "target": "id2", "relation": "rel" }}]
        }}
        """
        try:
            res = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config={'response_mime_type': 'application/json'}
            )
            data = json.loads(res.text)
            
            timestamp = datetime.now().isoformat()
            
            # Merge nodes
            existing_ids = {n.id for n in self.current_map.nodes}
            for n in data.get('new_nodes', []):
                if n['id'] not in existing_ids:
                    self.current_map.nodes.append(KnowledgeNode(**n, last_accessed=timestamp))
            
            # Merge edges
            for e in data.get('new_edges', []):
                # Check if edge already exists to prevent duplication
                if not any(edge.source == e['source'] and edge.target == e['target'] for edge in self.current_map.edges):
                    self.current_map.edges.append(KnowledgeEdge(**e))
            
            self._save_map()
        except Exception:
            pass  # background — silent failure is fine

    def generate_svg(self) -> str:
        """
        Generates a basic SVG visualization of the knowledge map.
        """
        width, height = 800, 600
        svg_parts = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']
        svg_parts.append('<rect width="100%" height="100%" fill="#1a1a1a"/>')
        
        # Simple circular layout for nodes
        import math
        nodes = self.current_map.nodes
        node_pos = {}
        for i, node in enumerate(nodes):
            angle = (i / max(len(nodes), 1)) * 2 * math.pi
            x = width/2 + 200 * math.cos(angle)
            y = height/2 + 200 * math.sin(angle)
            node_pos[node.id] = (x, y)
            
        # Draw edges
        for edge in self.current_map.edges:
            if edge.source in node_pos and edge.target in node_pos:
                x1, y1 = node_pos[edge.source]
                x2, y2 = node_pos[edge.target]
                svg_parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#444" stroke-width="1"/>')
                
        # Draw nodes
        for node in nodes:
            x, y = node_pos[node.id]
            color = "#00ffcc" if node.type == "component" else "#ffcc00"
            svg_parts.append(f'<circle cx="{x}" cy="{y}" r="30" fill="{color}" stroke="#fff" stroke-width="2"/>')
            svg_parts.append(f'<text x="{x}" y="{y+45}" fill="#fff" font-size="12" text-anchor="middle">{node.label}</text>')
            
        svg_parts.append('</svg>')
        
        active = self.workspace.get_active()
        output_path = os.path.join(active.root_dir, ".apex", "knowledge_graph.svg") if active else "data/knowledge_graph.svg"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            f.write("\n".join(svg_parts))
        return output_path

    async def get_pruned_context(self, query: str) -> str:
        """
        Optimizes context by selecting only relevant graph nodes.
        Uses Gemini-2.5-Flash-Lite to synthesize a high-density, low-token summary.
        """
        # 1. Get semantic matches from Chroma (L2)
        memories = await self.memory.chroma.search_memories(query, n_results=10)
        
        # 2. Identify relevant nodes
        relevant_node_ids = set()
        for m in memories:
            for node in self.current_map.nodes:
                if node.label.lower() in m['content'].lower() or node.id.lower() in m['content'].lower():
                    relevant_node_ids.add(node.id)
        
        # 3. Graph expansion (1st degree)
        expanded_ids = set(relevant_node_ids)
        for edge in self.current_map.edges:
            if edge.source in relevant_node_ids: expanded_ids.add(edge.target)
            if edge.target in relevant_node_ids: expanded_ids.add(edge.source)
            
        # 4. Build raw context
        raw_parts = []
        for node in self.current_map.nodes:
            if node.id in expanded_ids:
                raw_parts.append(f"[{node.label} ({node.type})]: {node.summary}")
        
        if not raw_parts: return ""

        # 5. High-Density Synthesis (Token Compression)
        if self.client:
            compression_prompt = f"""
            Compress the following knowledge graph entities into a high-density architectural context.
            Eliminate fluff. Focus on relations and technical facts relevant to the query: '{query}'
            
            ENTITIES:
            {chr(10).join(raw_parts)}
            
            Output a concise, structured context block (max 300 tokens).
            """
            try:
                res = self.client.models.generate_content(
                    model="gemini-2.5-flash-lite", 
                    contents=compression_prompt
                )
                return f"--- KNOWLEDGE GRAPH CONTEXT (COMPRESSED) ---\n{res.text.strip()}"
            except:
                return "--- KNOWLEDGE GRAPH CONTEXT ---\n" + "\n".join(raw_parts[:5])
        
        return "--- KNOWLEDGE GRAPH CONTEXT ---\n" + "\n".join(raw_parts[:5])
