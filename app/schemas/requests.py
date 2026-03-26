from pydantic import BaseModel, field_validator, ConfigDict, StrictStr


class BaseCndRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    cnpj: str


class EstadualRequest(BaseCndRequest):
    uf: StrictStr

    @field_validator("uf")
    @classmethod
    def validate_uf(cls, v: str) -> str:

        v = "".join(filter(str.isalpha, v)).upper()

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
