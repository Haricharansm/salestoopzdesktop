from pydantic import BaseModel
from typing import Any, Dict, Optional

class WorkspaceRequest(BaseModel):
    company_name: str
    offering: str
    icp: str

class AgentLaunchRequest(BaseModel):
    offering: Dict[str, Any]
    icp: Dict[str, Any]
    workspace_id: Optional[str] = None
