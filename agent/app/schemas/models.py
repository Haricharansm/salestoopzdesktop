from pydantic import BaseModel

class WorkspaceRequest(BaseModel):
    company_name: str
    offering: str
    icp: str
