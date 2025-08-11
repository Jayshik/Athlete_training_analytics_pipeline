from typing import Optional

from sqlmodel import Field, SQLModel


class GeneratedSessionStructure(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: Optional[str] = None
    description: Optional[str] = None
    generated_structure: str
    is_valid: bool
    version_model: str
    comment: Optional[str] = None
