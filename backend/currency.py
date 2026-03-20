from fastapi import FastAPI
import httpx
import os
from dotenv import load_dotenv
from model.CurrencyResponse import ExchangeRateResponse
load_dotenv()

app = FastAPI()
api_url = os.getenv("api_url")

@app.get("/api/base",response_model=ExchangeRateResponse)
async def getRates(base:str):
	url = api_url+base
	async with httpx.AsyncClient() as client:
		response = await client.get(url)
		data = response.json()
	data_unpacked = ExchangeRateResponse(**data)
	return data_unpacked
