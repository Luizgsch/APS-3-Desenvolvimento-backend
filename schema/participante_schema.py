from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ParticipanteBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nome: str = Field(min_length=1)
    email: EmailStr
    curso: str = Field(min_length=1)


class ParticipanteCreate(ParticipanteBase):
    pass


class ParticipanteUpdate(ParticipanteBase):
    """Atualização completa via PUT, com os mesmos campos obrigatórios."""


class ParticipanteRead(ParticipanteBase):
    model_config = ConfigDict(from_attributes=True, str_strip_whitespace=True)

    id: int = Field(gt=0)
