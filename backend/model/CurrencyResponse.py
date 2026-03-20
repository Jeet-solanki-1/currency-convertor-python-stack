from pydantic import BaseModel
from typing import Dict
class ExchangeRateResponse(BaseModel):
	base:str
	date:str
	rates:dict[str,float]



# Pydantic model for conversion response
class ConversionResult(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    converted_amount: float
    rate: float