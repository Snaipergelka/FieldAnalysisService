from pydantic import BaseModel


class AddNDVI(BaseModel):
    id: int


class FieldID(BaseModel):
    field_id: int
