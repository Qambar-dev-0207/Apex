from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class TaskStep(BaseModel):
    """
    Represents a single step in an execution plan.
    """
    id: int
    action: str
    description: str
    tool: Optional[str] = None
    input_data: Optional[str] = None
    dependencies: List[int] = []

class ExecutionPlan(BaseModel):
    """
    Represents a full execution plan decomposed by the Thinking Path.
    """
    task_plan: List[TaskStep]
    tools_required: List[str]
    requires_clarification: bool
    summary: str
    socratic_insight: Optional[str] = None

class CapabilityGap(BaseModel):
    """
    Represents a missing skill or MCP tool detected during codebase analysis.
    """
    id: str
    type: str # "skill" or "mcp"
    description: str
    suggested_name: str
    reason: str
    priority: int # 1-5

class ProjectManifest(BaseModel):
    """
    Tracks a specific project within the workspace.
    """
    name: str
    description: str
    root_dir: str
    goals: List[str]
    todos: List[Dict[str, Any]] = []
    file_tree: List[str] = []
    deadlines: List[Dict[str, Any]] = [] # [{"task": "X", "date": "2026-05-01", "risk": 0.1}]
    status: str = "active"

class BriefingReport(BaseModel):
    """
    A proactive morning strategy report.
    """
    date: str
    high_priority_tasks: List[str]
    risk_alerts: List[str]
    suggested_strategy: str
    spend_summary: str

class MemoryEntry(BaseModel):
    """
    Represents a single memory entry (conversation turn or task result).
    """
    role: str # user or assistant
    content: str
    metadata: Optional[Dict[str, Any]] = {}

class SessionContext(BaseModel):
    """
    Represents the active session context stored in Redis.
    """
    session_id: str
    history: List[MemoryEntry] = []
    last_plan: Optional[ExecutionPlan] = None

class Skill(BaseModel):
    """
    Represents a reusable execution pattern learned by the system.
    """
    name: str
    description: str
    query_pattern: str
    plan_template: ExecutionPlan
    usage_count: int = 1

class FailureRecord(BaseModel):
    """
    Logs an execution failure for future optimization.
    """
    timestamp: str
    tool: str
    input_data: str
    error: str
    session_id: str

class CodeSpec(BaseModel):
    """
    A detailed specification for a coding task.
    """
    task_description: str
    file_tree: List[str]
    interfaces: List[Dict[str, Any]]
    test_scenarios: List[str]
    architecture_notes: str

class ValidationResult(BaseModel):
    """
    Results of the code validation process.
    """
    success: bool
    test_output: str
    errors: Optional[List[str]] = []
    coverage: Optional[float] = None
    generated_code: str

class KnowledgeArtifact(BaseModel):
    """
    A high-density synthesized research report.
    """
    topic: str
    summary: str
    findings: List[Dict[str, Any]]
    sources: List[str]
    confidence_score: float

class SystemVitals(BaseModel):
    """
    Real-time hardware telemetry data.
    """
    cpu_percent: float
    gpu_percent: Optional[float] = None
    ram_percent: float
    temperature: Optional[float] = None
    status: str = "nominal" # nominal, warning, critical

class EmotionalState(BaseModel):
    """
    User's cognitive and emotional state.
    """
    sentiment: str = "neutral" # neutral, stressed, excited, frustrated
    cognitive_load: str = "low" # low, medium, high
    flow_active: bool = False
    velocity_mps: float = 0.0 # messages per second

class ApexState(BaseModel):
    """
    APEX's own affective state — mirrors / complements user state.
    """
    mood: str = "calm" # calm, curious, excited, focused, concerned, playful, skeptical
    energy: float = 0.6 # 0.0-1.0
    curiosity: float = 0.7 # 0.0-1.0
    confidence: float = 0.8 # 0.0-1.0
    response_style: str = "balanced" # terse, balanced, expansive, socratic
    flavor: str = "" # one-line emotional flavor for the response

class KnowledgeNode(BaseModel):
    id: str
    label: str
    type: str  # e.g., "component", "logic", "requirement", "user_pref"
    summary: str
    last_accessed: str

class KnowledgeEdge(BaseModel):
    source: str
    target: str
    relation: str # e.g., "depends_on", "implements", "prefers"

class KnowledgeMap(BaseModel):
    nodes: List[KnowledgeNode] = []
    edges: List[KnowledgeEdge] = []
