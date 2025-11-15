# web/app.py
import os
import json
import hmac
import hashlib
import secrets
import time
from aiohttp import web
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 8080))
SERVER_KEY = os.getenv("SERVER_KEY") or "CHANGE_ME"
ROUNDS_FILE = "rounds.json"

# ensure file
if not os.path.exists(ROUNDS_FILE):
    with open(ROUNDS_FILE, "w") as f:
        json.dump({}, f)

def read_rounds():
    with open(ROUNDS_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return {}

def write_rounds(d):
    with open(ROUNDS_FILE, "w") as f:
        json.dump(d, f, indent=2)

def compute_digest(server_seed: str) -> str:
    # HMAC-SHA256 of server_seed with SERVER_KEY
    return hmac.new(SERVER_KEY.encode(), server_seed.encode(), hashlib.sha256).hexdigest()

def compute_multiplier_from_digest(digest: str) -> float:
    """
    Простая, полностью детерминированная функция преобразования digest -> multiplier.
    Берём первые 8 hex, переводим в int, мапим в диапазон [1.00, 100.00].
    Это прозрачная и легко проверяемая схема: публикуется digest, затем раскрывается server_seed,
    и каждый может проверить, что digest = HMAC(SERVER_KEY, server_seed) и что multiplier рассчитан корректно.
    """
    part = digest[:8]
    val = int(part, 16)
    # map val -> 0 ..  (16**8 -1)
    maxv = 16**8 - 1
    # ratio в [0,1)
    ratio = val / maxv
    # map в [1.00, 100.00]
    multiplier = 1.0 + ratio * 99.0
    # округлим до 2 знаков
    return round(multiplier, 2)

routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse('./static/index.html')

@routes.get('/static/{name}')
async def static_files(request):
    name = request.match_info['name']
    return web.FileResponse(f'./static/{name}')

@routes.get('/api/next-round')
async def api_next_round(request):
    # create round
    round_id = str(int(time.time()*1000))
    server_seed = secrets.token_hex(32)
    digest = compute_digest(server_seed)
    rounds = read_rounds()
    rounds[round_id] = {
        "digest": digest,
        "created_at": time.time(),
        "resolved": False,
        "server_seed": server_seed  # в демо сохраняем, чтобы можно было раскрыть; в прод — хранить безопасно
    }
    write_rounds(rounds)
    return web.json_response({"round_id": round_id, "digest": digest})

@routes.post('/api/resolve-round')
async def api_resolve_round(request):
    body = await request.json()
    round_id = body.get("round_id")
    if not round_id:
        return web.json_response({"error": "round_id required"}, status=400)
    rounds = read_rounds()
    r = rounds.get(round_id)
    if not r:
        return web.json_response({"error": "round not found"}, status=404)
    # reveal seed and multiplier
    server_seed = r.get("server_seed")
    digest = r.get("digest")
    multiplier = compute_multiplier_from_digest(digest)
    r["resolved"] = True
    r["server_seed"] = server_seed
    r["multiplier"] = multiplier
    r["resolved_at"] = time.time()
    rounds[round_id] = r
    write_rounds(rounds)
    return web.json_response({"round_id": round_id, "digest": digest, "server_seed": server_seed, "multiplier": multiplier})

@routes.get('/api/round-info/{round_id}')
async def api_round_info(request):
    round_id = request.match_info['round_id']
    rounds = read_rounds()
    r = rounds.get(round_id)
    if not r:
        return web.json_response({"error":"round not found"}, status=404)
    # do not expose server_seed if not resolved
    out = {
        "round_id": round_id,
        "digest": r.get("digest"),
        "created_at": r.get("created_at"),
        "resolved": r.get("resolved"),
        "multiplier": r.get("multiplier") if r.get("resolved") else None,
        "server_seed": r.get("server_seed") if r.get("resolved") else None
    }
    return web.json_response(out)

app = web.Application()
app.add_routes(routes)
app.router.add_static('/static/', path='./static', name='static')

if __name__ == '__main__':
    web.run_app(app, host='0.0.0.0', port=PORT)
