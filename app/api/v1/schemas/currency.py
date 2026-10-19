from pydantic import BaseModel

from app.enums.currency import Currency


class ConvertResponse(BaseModel):
    amount: float
    base: Currency
    quote: Currency
    rate: float
    result: float
