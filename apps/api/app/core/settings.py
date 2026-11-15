"""Validate configuration before the application starts accepting requests."""

from pathlib import Path
from typing import Literal, Self
from urllib.parse import urlsplit

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIRECTORY = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SMS_",
        env_file=API_DIRECTORY / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    environment: Literal["development", "test", "staging", "production"] = "development"
    debug: bool = False
    enable_learning_endpoints: bool = False
    cors_origins: list[str] = Field(default_factory=list)

    @field_validator("cors_origins")
    @classmethod
    def validate_origins(cls, origins: list[str]) -> list[str]:
        normalized = []
        for origin in origins:
            candidate = origin.strip()
            parsed = urlsplit(candidate)
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or "*" in parsed.netloc
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path not in {"", "/"}
                or parsed.query
                or parsed.fragment
                or "?" in candidate
                or "#" in candidate
                or any(character.isspace() for character in candidate)
            ):
                raise ValueError(
                    "CORS origins must be exact HTTP(S) origins without paths or credentials"
                )
            # Accessing .port also rejects invalid port values.
            _ = parsed.port
            normalized.append(candidate.rstrip("/"))
        return list(dict.fromkeys(normalized))

    @model_validator(mode="after")
    def validate_deployed_settings(self) -> Self:
        if self.environment in {"staging", "production"}:
            if self.debug or self.enable_learning_endpoints:
                raise ValueError("Deployed environments cannot enable debug or learning endpoints")
            if any(urlsplit(origin).scheme != "https" for origin in self.cors_origins):
                raise ValueError("Deployed CORS origins must use HTTPS")
        return self

    @property
    def is_local(self) -> bool:
        return self.environment in {"development", "test"}
