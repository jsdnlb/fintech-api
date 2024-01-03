from pydantic import BaseModel, Field
from bson import ObjectId


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(str(v)):
            raise ValueError("Invalid ObjectId")
        return str(v)


class BaseSchema(BaseModel):
    id: ObjectIdStr = Field(alias="_id")

    class Config:
        populate_by_name = True
        json_encoders = {
            ObjectId: str,
        }
