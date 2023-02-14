from pydantic import BaseModel


class UserCreate(BaseModel):
    numOfPass: int
    numberPlate: str
    plateImg: str
