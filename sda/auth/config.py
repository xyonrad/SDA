from __future__ import annotations
'''
1. Enables self-referential types without quotes;
2. Allows mutual refs in the classes;
3. Reduces import cycles for type checking;
4. Lowers runtime cost;
'''

"""
File `config.py`

// TODO

v0.0.1: user credentials + API key live in .env (move to the database)
"""

from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

import os
import hashlib

PASS = "e759968ca9278b8dde9f515ff1957813343dc35dbd2e5f68b38b5a17e29fe541"
DEFAULT_STR = ""
DEV_HASH = { "dev": PASS }

def SHA256_hex(s: str) -> str:
    """
    Encoding the string 's' to the SHA256 hex
    """
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def verify_pass(password: str) -> str:
    """
    TODO
    """
    _hex = SHA256_hex(password)
    role, expected = list(map(list, DEV_HASH.items()))[0]
    if _hex == expected:
        return role
    return "user"

def profile_load(profile: str) -> None:
    """
    TODO
    """
    file_names = EnvFileNames()
    if profile == "dev" and Path(file_names.DEV).exists():
        load_dotenv(file_names.DEV, override=True)
    else:
        load_dotenv(file_names.USER, override=True)

# === TEST SIDE START ===

# === TEST SIDE END ===

@dataclass(frozen=True)
class Profiles:
    """
    TODO
    """
    USER: str = "user"
    DEV: str  = "dev"

@dataclass(frozen=True)
class DefaultDirectories:
    """
    TODO
    """
    root  = Path.cwd().resolve()

    '''
    If program starts in root (working directory) then "sda/" locates in current directory.
    Otherwise, program started in the .venv, then so we need to go to the parrent directory.
    '''
    SDA   = (root / "sda") if (root / "sda").exists() else (root.parent / "sda")
    DATA  = SDA / "data" / "data"
    CACHE = SDA / "data" / "cache"

@dataclass(frozen=True)
class EnvFields:
    SDA_PROFILE: str     = "SDA_PROFILE"
    SDA_DATA_DIR: str    = "SDA_DATA_DIR"
    SDA_CACHE_DIR: str   = "SDA_CACHE_DIR"
    SDA_LOG_LEVEL: str   = "SDA_LOG_LEVEL"

    SDA_USER_LOGIN: str  = "SDA_USER_LOGIN"
    SDA_USER_PASS: str   = "SDA_USER_PASS"
    SDA_LH_KEY: str      = "SDA_LH_KEY"

    PG_HOST: str         = "PG_HOST"
    PG_PORT: str         = "PG_PORT"
    PG_DB: str           = "PG_DB"
    PG_USER: str         = "PG_USER"
    PG_PASS: str         = "PG_PASS"

    # Copernicus fields
    CDSE_USER: str       = "CDSE_USER"
    CDSE_PASS: str       = "CDSE_PASS"
    CDSE_AUTH_TOKEN: str = "CDSE_AUTH_TOKEN"
 
@dataclass(frozen=True)
class LogLevels:
    """
    TODO
    """
    INFO: str  = "INFO"
    DEBUG: str = "DEBUG"

@dataclass(frozen=True)
class EnvFileNames:
    """
    TODO
    """
    USER: str = ".env"
    DEV: str  = ".env.dev"

@dataclass(frozen=True)
class PostgresDefaults:
    """
    TODO
    """
    HOST: str = "localhost"
    PORT: int = 5432
    DB: str   = "sda"
    USER: str = "sda"
    PASS: str = DEFAULT_STR


load_dotenv()

class Config(BaseSettings):
    """
    Runtime config.
    v0.0.1: user credentials + localhost API key live in .env
    """
    model_config = SettingsConfigDict(extra="ignore")
    EF           = EnvFields()
    EFN          = EnvFileNames()
    PD           = PostgresDefaults()
    LL           = LogLevels()
    DD           = DefaultDirectories()
    P            = Profiles()

    profile: str    = Field(default=P.USER, alias=EF.SDA_PROFILE)
    data_dir: str   = Field(default=str(DD.DATA), alias=EF.SDA_DATA_DIR)
    cache_dir: str  = Field(default=str(DD.CACHE), alias=EF.SDA_CACHE_DIR)
    log_level: str  = Field(default=LL.DEBUG, alias=EF.SDA_LOG_LEVEL)

    user_login: str = Field(default=P.USER, alias=EF.SDA_USER_LOGIN)
    user_pass: str  = Field(default=DEFAULT_STR, alias=EF.SDA_USER_PASS)
    api_key: str    = Field(default=DEFAULT_STR, alias=EF.SDA_LH_KEY)

    pg_host: str    = Field(default=PD.HOST, alias=EF.PG_HOST)
    pg_port: int    = Field(default=PD.PORT, alias=EF.PG_PORT)
    pg_db: str      = Field(default=PD.DB, alias=EF.PG_DB)
    pg_user: str    = Field(default=PD.USER, alias=EF.PG_USER)
    pg_pass: str    = Field(default=PD.PASS, alias=EF.PG_PASS)

    cdse_user: str  = Field(default=DEFAULT_STR, alias=EF.CDSE_USER)
    cdse_pass: str  = Field(default=DEFAULT_STR, alias=EF.CDSE_PASS)
    cdse_token: str = Field(default=DEFAULT_STR, alias=EF.CDSE_AUTH_TOKEN)

    @property
    def pg_dsn(self) -> str:
        """
        Construct a PostgreSQL SQLAlchemy DSN (Data Source Name)
        for driver `psycopg`.

        ## Usage:
            `Config().pg_dsn` -> returns a formed DSN string for engine.

        ## Format:
            `postgresql+psycopg://user:pass@host:port/db`
        """
        return f"postgresql+psycopg://{self.pg_user}:{self.pg_pass}@{self.pg_host}:{self.pg_port}/{self.pg_db}"


def get_config(profile: str | None = Profiles.USER) -> Config:
    p = profile or os.getenv(EnvFields.SDA_PROFILE, Profiles.USER)
    profile_load(p)
    return Config()
