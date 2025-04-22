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
    if score>80 and cex<10: return "🟢 Low"
    if score>50:              return "🟡 Medium"
    return "🔴 High"
