from pydantic import BaseModel
from typing import Dict
class ExchangeRateResponse(BaseModel):
	base:str
	date:str
	rates:dict[str,float]



