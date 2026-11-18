from datetime import date, time

from pydantic import BaseModel, ConfigDict, Field


class EventoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    titulo: str = Field(min_length=1)
    descricao: str = Field(min_length=1)
    data: date
    horario: time
    local: str = Field(min_length=1)
    capacidade: int = Field(gt=0)
    categoria: str = Field(min_length=1)


class EventoCreate(EventoBase):
    pass


class EventoUpdate(EventoBase):
    """Atualização completa via PUT, com os mesmos campos obrigatórios."""


class EventoRead(EventoBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int = Field(gt=0)
