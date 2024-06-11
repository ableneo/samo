from pydantic import BaseModel


class Prompt(BaseModel):
    entity: str
    instruction: str
