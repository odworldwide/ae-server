# creative_geo.py
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import math, time

# Pick five “sections” on the map (world view).
# You can move these wherever you like. (lon, lat)
REGION_ANCHORS = {
    "mainstream":  (-73.9857, 40.7580),  # NYC-ish
    "tiktok":      (139.6917, 35.6895),  # Tokyo-ish
    "gallery":     (2.3522,   48.8566),  # Paris-ish
    "collectors":  (-0.1276,  51.5072),  # London-ish
    "niche":       (18.4233, -33.9180),  # Cape Town-ish
}

EVENT_TO_REGION = {
    "teaser":           "niche",
    "collab_reveal":    "mainstream",
    "critic_preview":   "gallery",
    "drop":             None,          # go to home region (dominant following)
    "record_sale":      "collectors",
    "controversy":      "mainstream",
    "award":            "gallery",
    "platform_boost":   "tiktok",
    "supply_extension": "collectors",
}

def dominant_region(following: Optional[Dict[str, float]]) -> Optional[str]:
    if not following: return None
    return max(following.items(), key=lambda kv: kv[1])[0]

def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def interpolate(lon1, lat1, lon2, lat2, steps: int) -> List[Tuple[float,float]]:
    return [(lerp(lon1, lon2, t), lerp(lat1, lat2, t)) for t in [i/steps for i in range(1, steps+1)]]

def build_creative_points(track: dict) -> List[dict]:
    """
    Input: native creative track dict
      - needs: beats:[{t, event, delta?}], optional: following:{region:weight}
    Output: list of GeoJSON Point features (ordered).
    """
    beats = track.get("beats", [])
    following = track.get("following") or {}
    home = dominant_region(following) or "mainstream"

    # start just “offshore” from home so you see movement
    hx, hy = REGION_ANCHORS.get(home, REGION_ANCHORS["mainstream"])
    start = (hx - 10.0, hy)  # shove west 10° to animate in
    cur_lon, cur_lat = start

    features = []
    ts = int(time.time() * 1000)

    for i, beat in enumerate(beats):
        ev = beat.get("event")
        # decide target region for this beat
        target_region = EVENT_TO_REGION.get(ev)
        if target_region is None:
            target_region = home  # e.g., drop goes to home followers

        tx, ty = REGION_ANCHORS.get(target_region, (cur_lon, cur_lat))

        # steps: short hops for small events, longer for big moments
        steps = 4 if ev in ("teaser", "critic_preview") else 8
        for (lon, lat) in interpolate(cur_lon, cur_lat, tx, ty, steps):
            features.append({
                "type": "Feature",
                "properties": {
                    "artist": track.get("artist"),
                    "release": track.get("release"),
                    "event": ev,
                    # you can pipe hype/press/virality here if you want:
                    "hype": beat.get("delta", {}).get("hype", 0),
                    "press": beat.get("delta", {}).get("press", 0),
                    "virality": beat.get("delta", {}).get("virality", 0.0),
                    # optional: proximity block for your text overlay
                    "proximity": [{
                        "name": target_region.capitalize(),
                        "country": "",
                        "lat": ty,
                        "lon": tx,
                        "distance": 0.0
                    }],
                    "timestamp": ts
                },
                "geometry": { "type": "Point", "coordinates": [lon, lat] }
            })
            ts += 200  # ~0.2s between points; adjust to taste

        cur_lon, cur_lat = tx, ty

    return features
