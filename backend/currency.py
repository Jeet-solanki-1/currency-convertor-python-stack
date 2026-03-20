from fastapi import FastAPI, HTTPException
import httpx
import os
from dotenv import load_dotenv
from model.CurrencyResponse import ExchangeRateResponse, ConversionResult
from cache import ManualCache
from decimal import Decimal, ROUND_HALF_UP

load_dotenv()

app = FastAPI()
api_url = os.getenv("api_url")
cache = ManualCache(ttl_seconds=3600)

@app.get("/api/base", response_model=ExchangeRateResponse)
async def getRates(base: str):
    cache_data = await cache.get(base)
    if cache_data:
        return ExchangeRateResponse(**cache_data)
    
    url = api_url + base
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
    
    await cache.set(base, data)
    data_unpacked = ExchangeRateResponse(**data)
    return data_unpacked

@app.get("/api/convert", response_model=ConversionResult)
async def convert_currency(
    from_curr: str = "USD", 
    to_curr: str = "EUR",  # Changed from IND to EUR (more common)
    amount: float = 1.0
):
    try:
        rates_data = await getRates(from_curr)
        
        if not rates_data or not rates_data.rates:
            raise HTTPException(status_code=500, detail="Unable to fetch exchange rates")
        
        # Fixed: to_curr.upper() not to_currency
        rate = rates_data.rates.get(to_curr.upper())
        
        if rate is None:
            raise HTTPException(
                status_code=404,  # Changed to 404 (Not Found)
                detail=f"Currency {to_curr.upper()} not found"  # Fixed variable name
            )
        
        # Fixed: Variable names
        amount_decimal = Decimal(str(amount))
        rate_decimal = Decimal(str(rate))
        converted = amount_decimal * rate_decimal  # Fixed: was "convterd"
        
        # Fixed: converted_rounded not convterd_rounded
        converted_rounded = converted.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        
        return ConversionResult(
            from_currency=from_curr.upper(),
            to_currency=to_curr.upper(),
            original_amount=amount,
            converted_amount=float(converted_rounded),
            rate=rate  # Fixed: was "rates" should be "rate"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Fixed: Better error message
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")

@app.get("/api/cache/stats")
async def get_cache_stats():
    return cache.get_stats()

@app.delete("/api/cache/{currency}")
async def evict_cache(currency: str):
    """Manually evict cache for a currency"""
    await cache.evict(currency.upper())
    return {"message": f"Cache evicted for {currency}"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "cache_size": cache.get_stats()["size"]}