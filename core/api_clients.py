import aiohttp
from .cache import simple_cache

BASE_BUBBLE = "https://api-legacy.bubblemaps.io"
COINGECKO = "https://api.coingecko.com/api/v3"
PLATFORMS = {"eth":"ethereum","bsc":"binance-smart-chain","sol":"solana"}

@simple_cache()
async def fetch_bubble(chain, addr):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{BASE_BUBBLE}/map-data?token={addr}&chain={chain}") as r:
            return await r.json() if r.status==200 else None

@simple_cache()
async def fetch_meta(chain, addr):
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{BASE_BUBBLE}/map-metadata?chain={chain}&token={addr}") as r:
            if r.status!=200: return None
            d = await r.json()
            return {
                "score":d.get("decentralisation_score"),
                "cex": d["identified_supply"]["percent_in_cexs"],
                "contract": d["identified_supply"]["percent_in_contracts"],
            }

@simple_cache()
async def fetch_market(chain, addr):
    plat = PLATFORMS.get(chain)
    if not plat: return None
    async with aiohttp.ClientSession() as s:
        async with s.get(f"{COINGECKO}/coins/{plat}/contract/{addr}") as r:
            if r.status!=200: return None
            md = (await r.json()).get("market_data", {})
            return {
                "price": md["current_price"]["usd"],
                "vol": md["total_volume"]["usd"],
                "cap": md["market_cap"]["usd"],
            }
