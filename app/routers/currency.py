import httpx
from fastapi import APIRouter, HTTPException, Query

from app.enums.currency import Currency
from app.schemas.currency import ConvertResponse
from app.services import currency as currency_service

router = APIRouter(prefix="/currency", tags=["currency"])


@router.get("/convert", response_model=ConvertResponse)
async def convert(
    amount: float = Query(gt=0),
    base: Currency = Currency.USD,
    quote: Currency = Currency.default(),
):
    try:
        rate = float(currency_service.get_rate(base, quote))
    except httpx.HTTPError:
        raise HTTPException(status_code=502, detail="Failed to retrieve exchange rates.")

    return ConvertResponse(
        amount=amount,
        base=base,
        quote=quote,
        rate=rate,
        result=round(amount * rate, 2),
    )
