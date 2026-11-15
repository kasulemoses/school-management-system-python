"""Fictional student input for the development-only validation checkpoint."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class StudentInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    first_name: str = Field(strict=True, min_length=1, max_length=100, examples=["Amina"])
    last_name: str = Field(strict=True, min_length=1, max_length=100, examples=["Example"])
    admission_number: str = Field(strict=True, min_length=1, max_length=50, examples=["DEMO-0042"])


class StudentValidationResponse(BaseModel):
    valid: Literal[True] = True
    persisted: Literal[False] = False
    student: StudentInput
