from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import sqlite3
import json
import os
import re
import threading, time, random

# --- Creative "fake geography" adapter ---------------------------------------
from typing import Optional, Dict, List, Tuple

# anchor long/lat per audience region (lon, lat)
REGION_ANCHORS: Dict[str, Tuple[float, float]] = {
    "gallery":  (-73.9857, 40.7580),   # NYC-ish
    "tiktok":      (139.6917, 35.6895),   # Tokyo-ish
    "mainstream":     (2.3522,   48.8566),   # Paris-ish
    "collectors":  (-0.1276,  51.5072),   # London-ish
    "niche":       (18.4233, -33.9180),   # Cape Town-ish
}

# which region a given event should “aim” toward
EVENT_TO_REGION: Dict[str, Optional[str]] = {
    "teaser":           "niche",
    "collab_reveal":    "mainstream",
    "critic_preview":   "gallery",
    "drop":             None,             # home region (dominant following)
    "record_sale":      "collectors",
    "controversy":      "mainstream",
    "award":            "gallery",
    "platform_boost":   "tiktok",
    "supply_extension": "collectors",
}

def _dominant_region(following: Optional[Dict[str, float]]) -> Optional[str]:
    if not following:
        return None
    return max(following.items(), key=lambda kv: kv[1])[0]

def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def _interpolate(lon1: float, lat1: float, lon2: float, lat2: float, steps: int) -> List[Tuple[float, float]]:
    return [(_lerp(lon1, lon2, i/steps), _lerp(lat1, lat2, i/steps)) for i in range(1, steps+1)]

def creative_track_to_points(track: Dict) -> List[Dict]:
    """
    Convert a creative release JSON (with beats) into an array of GeoJSON Point Features
    that your Mapbox+p5 visual understands.
    """
    beats = track.get("beats") or []
    following = track.get("following") or {}
    home = _dominant_region(following) or "mainstream"

    hx, hy = REGION_ANCHORS.get(home, REGION_ANCHORS["mainstream"])
    # start slightly “offshore” so there’s immediate motion
    cur_lon, cur_lat = hx - 10.0, hy

    features: List[Dict] = []
    ts = 0  # simple monotonic timestamp per point

    for beat in beats:
        ev = (beat.get("event") or "").strip()
        target_region = EVENT_TO_REGION.get(ev)
        if target_region is None:   # e.g. drop → go to home
            target_region = home

        tx, ty = REGION_ANCHORS.get(target_region, (cur_lon, cur_lat))

        steps = 4 if ev in ("teaser", "critic_preview") else 8
        for (lon, lat) in _interpolate(cur_lon, cur_lat, tx, ty, steps):
            features.append({
                "type": "Feature",
                "properties": {
                    "artist":   track.get("artist"),
                    "release":  track.get("release"),
                    "event":    ev,
                    "hype":     beat.get("delta", {}).get("hype", 0),
                    "press":    beat.get("delta", {}).get("press", 0),
                    "virality": beat.get("delta", {}).get("virality", 0.0),
                    # your visual reads this block for labels/arrows
                    "proximity": [{
                        "name":     (target_region or home).capitalize(),
                        "country":  "",
                        "lat":      ty,
                        "lon":      tx,
                        "distance": 0.0
                    }],
                    "timestamp": ts
                },
                "geometry": { "type": "Point", "coordinates": [lon, lat] }  # lon,lat
            })
            ts += 200
        cur_lon, cur_lat = tx, ty

    return features
# -------------------------------------------------------------------------------


DATA_PATH = os.path.join(os.path.dirname(__file__),
                         "release_data",
                         "nova_aria__chromatic_drift.json")


dirname = os.path.dirname(__file__)
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

CORS(app, resources={r"/*": {"origins": "*"}})

# shared state + lock
_release_state = {
    "artist": "—",
    "release": "—",
    "event": "",
    "hype": 0.0,          # 0..100
    "press": 0.0,         # 0..100
    "virality": 0.0,      # 0..1
    "listing_pressure": 0.10,  # 0..1, trail width driver
    "following": {"mainstream":0.3,"tiktok":0.3,"gallery":0.2,"collectors":0.15,"niche":0.05},
    # optional extras you may emit later
    "sold": 0, "editions": 0, "floor": None
}
_release_lock = threading.Lock()
_creative_thread = None

def _load_release_seed():
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            try:
                data = json.load(f)
                return {
                    "artist": data.get("artist", _release_state["artist"]),
                    "release": data.get("release", _release_state["release"]),
                    "following": data.get("following", _release_state["following"]),
                }
            except Exception as e:
                print("release seed load error:", e)
    return {}

def _apply_decay(rs, dt=1.0):
    # gentle decay toward zero so values don’t get stuck high
    rs["hype"] = max(0.0, rs["hype"] - 0.12*dt)
    rs["press"] = max(0.0, rs["press"] - 0.08*dt)
    rs["virality"] = max(0.0, rs["virality"] - 0.0015*dt)
    # small drift on listing unless market heats it
    rs["listing_pressure"] = max(0.02, rs["listing_pressure"] - 0.004*dt)

def _apply_market_influence(rs):
    """Use your in-memory market snapshot (that server.update_market sets)."""
    global market
    if isinstance(market, dict):
        bids = len(market.get("bid_list", []) or [])
        asks = len(market.get("ask_list", []) or [])
        price = market.get("price")
        bid_pressure = (bids / asks) if asks else (2.0 if bids else 0.0)

        # bids/asks heat the room
        rs["hype"] += min(2.0, 0.15 * bids)
        rs["listing_pressure"] = min(0.6, rs["listing_pressure"] + 0.02 * bid_pressure)

        # crude “floor” inference from price momentum (optional)
        if isinstance(price, (int, float)):
            if rs.get("_prev_price") is not None:
                dp = price - rs["_prev_price"]
                if dp > 0:
                    rs["floor"] = (rs.get("floor") or price) + dp*0.4
                else:
                    rs["floor"] = (rs.get("floor") or price) + dp*0.2
            rs["_prev_price"] = price

def _fire_micro_event(rs):
    roll = random.random()
    if roll < 0.20:
        rs["event"] = "platform_boost"
        rs["virality"] = min(1.0, rs["virality"] + 0.03 + random.random()*0.04)
    elif roll < 0.38:
        rs["event"] = "collab_reveal"
        rs["hype"] += 6 + random.random()*8
    elif roll < 0.54:
        rs["event"] = "critic_preview"
        rs["press"] += 6 + random.random()*6
    elif roll < 0.64:
        rs["event"] = "record_sale"
        rs["listing_pressure"] = min(0.6, rs["listing_pressure"] + 0.05)
        # nudge floor upward
        base = rs.get("floor") or 100
        rs["floor"] = base + (4 + random.random()*12)
    elif roll < 0.82:
        rs["event"] = "teaser"
        rs["hype"] += 3 + random.random()*4
    else:
        rs["event"] = ""  # idle

def _creative_daemon():
    """
    Background daemon that periodically updates the release state with new events,
    applies decay and market influence, and seeds initial values from JSON.
    Intended to simulate ongoing creative and market activity.
    """
    # seed labels/following from JSON once
    seed = _load_release_seed()
    with _release_lock:
        _release_state.update(seed)

    next_micro = time.time() + random.uniform(3, 7)
    last_tick = time.time()

    while True:
        now = time.time()
        dt = max(0.2, now - last_tick)
        # Example body: apply decay and sleep to simulate background processing
        with _release_lock:
            _apply_decay(_release_state, dt)
            _apply_market_influence(_release_state)
            _fire_micro_event(_release_state)
        last_tick = now
        time.sleep(1.0)

def add_cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return resp

# cors = CORS(app)
hurricane = []
market = {}

def new_hurricane():
	global hurricane
	hurricane=[]

def new_point(p):
	global hurricane
	hurricane.append(p)

def update_market(market_state):
	global market
	market = market_state

@app.route("/release", methods=["GET"])
def get_release():
	if not os.path.exists(DATA_PATH):
		return jsonify([])  # points array expected by the Mapbox view
	with open(DATA_PATH, "r") as f:
		track = json.load(f)
	features = creative_track_to_points(track)  # the adapter we added earlier
	return jsonify(features)

@app.route("/release_state", methods=["GET"])
def get_release_state():
    if not os.path.exists(DATA_PATH):
        return jsonify({})
    with open(DATA_PATH, "r") as f:
        track = json.load(f)

    last = (track.get("beats") or [])[-1] if track.get("beats") else {}
    delta = last.get("delta", {}) if last else {}
    state = {
        "artist": track.get("artist"),
        "release": track.get("release"),
        "event": last.get("event", ""),
        "hype": float(delta.get("hype", 0)),
        "press": float(delta.get("press", 0)),
        "virality": float(delta.get("virality", 0)),
        "following": track.get("following", {"mainstream":0.4,"tiktok":0.3,"gallery":0.1,"collectors":0.1,"niche":0.1}),
        "listing_pressure": 0.15
    }
    return jsonify(state)

@app.route("/userchat", methods=["POST"])
def post_chat():
	# u can't say that
	block = False
	blacklist = ["testblacklist", "nigger","nigga", "nigg", "fag", "faggot", "bitch", "whore", "retard", "cunt", "paki", "kike", "coon", "gook"]
	user = request.form['user']
	chat_string = request.form['chat_string']
	for word in blacklist:
		if word in chat_string or word in user:
			block = True
			print('blocked')
	conn = None
	chat = []
	if block == False :
		print('adding to chat')
		try:
			conn = sqlite3.connect(os.path.join(dirname, 'fud.db'))
			c = conn.cursor()
			with conn:
				c.execute("INSERT INTO chat (user,chatString, entityType) VALUES (?,?,?)", (user, chat_string, 'person'))
		except sqlite3.Error as e:
			print(e)
		finally:
			if conn:
				conn.close()
		return 'chat'
	else:
		return "you can't say that"


@app.route("/email", methods=["POST"])
def email():
	email = request.form['email']
	email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
	if(re.search(email_pattern,email)):
		conn = None
		try:
			conn = sqlite3.connect(os.path.join(dirname, 'mail.db'))
			c = conn.cursor()
			with conn:
				c.execute("INSERT INTO mail (email) VALUES (?)", (email,))
		except sqlite3.Error as e:
			print(e)
		finally:
			if conn:
				conn.close()
		return 'valid email'

	else:
		return 'invalid email'


@app.route("/chat", methods=["GET"])
def get_chat():
	conn = None
	chat = []
	try:
		conn = sqlite3.connect(os.path.join(dirname, 'fud.db'))
		c = conn.cursor()
		with conn:
			chatBuf = c.execute('''SELECT * FROM (SELECT * FROM chat ORDER BY id DESC LIMIT 20)Var1 ORDER BY id ASC''')
			for row in chatBuf:
				chat.append({
					'timestamp': row[1],
					'agent': row[2],
					'chat': row[3],
					'entityType': row[4]
				})
		return json.dumps(chat, indent=4, sort_keys=True)

	except sqlite3.Error as e:
		print(e)
	finally:
		if conn:
			conn.close()
	return 'chat'


@app.route("/hurricane", methods=["GET"])
def get_hurricane():
	global hurricane
	return json.dumps(hurricane, indent=4, sort_keys=True)


@app.route("/market", methods=["GET"])
def get_market():
	global market
	return json.dumps(market, indent=4, sort_keys=True)


@app.route("/", methods=["GET"])
def get_all():
	return "blah"

def run():
	app.run(port=5050, host="0.0.0.0", use_reloader=False)

# at the bottom of server.py, after defining get_chat, get_market, get_hurricane:
app.add_url_rule("/fud/chat",      view_func=get_chat,      methods=["GET"])
app.add_url_rule("/fud/market",    view_func=get_market,    methods=["GET"])
app.add_url_rule("/fud/hurricane", view_func=get_hurricane, methods=["GET"])
app.add_url_rule("/fud/userchat",  view_func=post_chat,     methods=["POST"])
# New ting
app.add_url_rule("/fud/release",       view_func=get_release,       methods=["GET"])
app.add_url_rule("/fud/release_state", view_func=get_release_state, methods=["GET"])

