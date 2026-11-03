from typing import ClassVar

from pydantic import BaseModel, model_validator


class UpdateSchemaBase(BaseModel):
    nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="before")
    @classmethod
    def reject_null_values(cls, data):
        if isinstance(data, dict):
            for field, value in data.items():
                if value is None and field not in cls.nullable_fields:
                    raise ValueError(f"{field} cannot be null")
        return data
