from typing import List, Dict, Tuple

GLOBAL_FAVS: Dict[Tuple[str,str],int] = {}
TOTAL = 0

def update_global_on_add(c,a):
    GLOBAL_FAVS[(c,a)] = GLOBAL_FAVS.get((c,a),0)+1

def update_global_on_remove(c,a):
    k=(c,a)
    GLOBAL_FAVS[k]-=1
    if GLOBAL_FAVS[k]<=0: GLOBAL_FAVS.pop(k)

def increment_scans():
    global TOTAL; TOTAL+=1

def get_stats(user_favs:List[dict]) -> str:
    return (
        f"📊 **Bot Stats** 📊\n\n"
        f"Global scans: {TOTAL}\n"
        f"Your favs: {len(user_favs)}\n"
        f"Unique global favs: {len(GLOBAL_FAVS)}"
    )

def compute_risk(score, vol, cex, contract):
    # Weighted multi-factor analysis
    risk_score = (
        0.5 * (score/100) +          # Decentralization (50% weight)
        0.2 * (1 - cex/100) +        # CEX exposure (20% weight)
        0.2 * (1 - contract/100) +   # Contract risk (20% weight)
        0.1 * (min(vol/5e6, 1))     # Liquidity (10% weight, $5M cap)
    )
    if risk_score >= 0.75:
        return "🟢 Low"              # >75% composite score
    elif risk_score >= 0.55:
        return "🟡 Medium"           # 55-74% composite score
    elif risk_score >= 0.35:
        return "🟠 Elevated"         # New tier for granularity
    else:
        return "🔴 High"             # <35% composite score
