from pydantic import BaseModel, field_validator, ConfigDict, StrictStr
from typing import Optional, List
from enum import Enum
from datetime import datetime


class LogLevel(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class BaseCndRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cnpj: str


class EstadualRequest(BaseCndRequest):
    uf: StrictStr

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v: str) -> str:

        v = "".join(filter(str.isalpha, v)).lower()

        if len(v) != 2:
            raise ValueError("UF deve conter exatamente 2 letras")

        return v


class MunicipalRequest(EstadualRequest):
    municipio: StrictStr

    @field_validator("municipio")
    @classmethod
    def validate_municipio(cls, v: str) -> str:
        v = "".join(filter(str.isalpha, v))
        return v.lower().strip().replace(" ", "_")


class LogFilter(BaseModel):
    tipo_cnd: Optional[List[StrictStr]] = []
    cnpj: Optional[List[StrictStr]] = []
    error_type: Optional[List[StrictStr]] = []
    level: Optional[List[LogLevel]] = []
    init_date: Optional[StrictStr] = None
    end_date: Optional[StrictStr] = None

    @field_validator("init_date", "end_date")
    @classmethod
    def validate_date(cls, v: Optional[str]):
        if v is None:
            return v

        try:
            datetime.strptime(v, "%d-%m-%Y")
        except ValueError:
            raise ValueError("Date must be in format DD-MM-YYYY")

        return v

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, v):
        if isinstance(v, list):
            return [item.upper() if isinstance(item, str) else item for item in v]
        return v

    model_config = ConfigDict(extra="forbid")
