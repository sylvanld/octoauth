from datetime import datetime

from pydantic import BaseModel


def datetime_to_iso_8601(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


class BaseDTO(BaseModel):
    class Config:
        orm_mode = True
        json_encoders = {datetime: datetime_to_iso_8601}
