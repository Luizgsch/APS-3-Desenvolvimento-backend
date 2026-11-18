from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class InscricaoCreate(BaseModel):
    evento_id: int = Field(gt=0)
    participante_id: int = Field(gt=0)


class InscricaoRead(InscricaoCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    data_inscricao: date
