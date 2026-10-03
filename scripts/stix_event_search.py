"""Reproducible search for bright, multi-pulse STIX flares (event selection, OE2).

Uses only the public, read-only API of the STIX data center (https://datacenter.stix.i4ds.net):
the flare list, the quick-look light curves (4 s, five bands) and the ephemeris. Everything is
cached under results/stix_events/ (git-ignored).

Selection logic
1. Flare list sorted by the 50-84 keV quick-look band; entries within 40 min are one event.
2. Reject particle-background "events": a flare has net 15-25 keV counts >= net 50-84 keV counts.
3. Keep events with net 25-50 keV peak counts >= MIN_LC3 per 4 s.
4. In the quick-look 25-50 keV curve (pre-flare background subtracted), find pulses: peaks with
   prominence >= max(15 % of the maximum, 5 sqrt(N)), at least 8 s apart, where the curve exceeds
   10 % of its maximum, and not within 8 s of an attenuator / rate-control (RCR) change.
5. Per pulse: net counts in 25-84 keV between the neighbouring minima.

Quick-look counts are compressed and summed over detectors; they rank events, they are not
the science data used for spectroscopy.

    .venv/bin/python scripts/stix_event_search.py
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import time
import urllib.parse
import urllib.request

import numpy as np
from scipy.signal import find_peaks

HOST = "https://datacenter.stix.i4ds.net"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "stix_events")
MIN_LC3 = 20000          # net 25-50 keV peak counts per 4 s
N_CANDIDATES = 30
WINDOW_MIN = 15          # minutes either side of the peak


def post(endpoint: str, fields: dict, cache: str, timeout: int = 120):
    path = os.path.join(OUT, "cache", cache)
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    data = urllib.parse.urlencode(fields).encode()
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(HOST + endpoint, data=data), timeout=timeout) as r:
                out = json.load(r)
            break
        except Exception:  # network hiccup: retry politely
            if attempt == 2:
                raise
            time.sleep(3)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(out, fh)
    time.sleep(0.5)
    return out


def flare_list() -> list:
    flares = {}
    d = dt.date(2021, 1, 1)
    while d < dt.date.today():
        e = (d.replace(day=1) + dt.timedelta(days=95)).replace(day=1)
        lst = post("/api/request/flare-list", dict(start_utc=d.isoformat() + "T00:00:00",
                                                  end_utc=e.isoformat() + "T00:00:00", sort="LC4"),
                   "flarelist_%s.json" % d.isoformat())
        for f in lst:
            flares[f["flare_id"]] = f
        d = e
    return list(flares.values())


def net(f: dict, band: int) -> float:
    return max((f.get("LC%d_PEAK_COUNTS_4S" % band) or 0) - (f.get("LC%d_BKG_COUNTS_4S" % band) or 0), 0)


def candidates(flares: list) -> list:
    rows = []
    for f in flares:
        try:
            t = dt.datetime.fromisoformat(f["peak_UTC"][:19])
        except (TypeError, ValueError):
            continue
        r = dict(flare_id=f["flare_id"], peak=t, goes=f.get("GOES_class"), stix_class=f.get("goes_estimated_mean_class"),
                 att_in=f.get("att_in"), lc2=net(f, 2), lc3=net(f, 3), lc4=net(f, 4))
        if r["lc2"] >= r["lc4"] and r["lc3"] >= MIN_LC3:
            rows.append(r)
    rows.sort(key=lambda r: -r["lc3"])
    events = []
    for r in rows:
        if all(abs((r["peak"] - e["peak"]).total_seconds()) > 2400 for e in events):
            events.append(r)
    return events


def pulses(lc: dict) -> dict:
    t = np.array(lc["unix_time"])
    c = {int(k): np.array(v, float) for k, v in lc["light_curves"].items()}
    rcr = np.array(lc["rcr"])
    pre = slice(0, max(10, int(0.15 * t.size)))
    b3 = np.median(c[3][pre])
    b4 = np.median(c[4][pre])
    s3 = np.clip(c[3] - b3, 0, None)
    s34 = s3 + np.clip(c[4] - b4, 0, None)
    peak = s3.max()
    prom = max(0.15 * peak, 5.0 * math.sqrt(peak + b3))
    idx, props = find_peaks(s3, prominence=prom, distance=2)
    changes = t[np.nonzero(np.diff(rcr))[0] + 1]
    keep = [i for i in idx if s3[i] > 0.1 * peak and not np.any(np.abs(changes - t[i]) <= 8.0)]
    out = []
    for n, i in enumerate(keep):
        lo = keep[n - 1] if n else max(0, i - 10)
        hi = keep[n + 1] if n + 1 < len(keep) else min(t.size - 1, i + 10)
        a = lo + int(np.argmin(s3[lo:i + 1])) if n else lo
        b = i + int(np.argmin(s3[i:hi + 1])) if n + 1 < len(keep) else hi
        out.append(dict(t=dt.datetime.utcfromtimestamp(t[i]).isoformat(timespec="seconds"),
                        peak_25_50=float(s3[i]), counts_25_84=float(np.sum(s34[a:b + 1]))))
    gaps = np.diff([t[i] for i in keep]) if len(keep) > 1 else np.array([])
    return dict(n_pulses=len(out), pulses=out, median_gap_s=float(np.median(gaps)) if gaps.size else None,
                rcr_changes=int(changes.size), bkg_25_50=float(b3))


def main():
    os.makedirs(OUT, exist_ok=True)
    events = candidates(flare_list())[:N_CANDIDATES]
    table = []
    for e in events:
        t0 = (e["peak"] - dt.timedelta(minutes=WINDOW_MIN)).isoformat()
        t1 = (e["peak"] + dt.timedelta(minutes=WINDOW_MIN)).isoformat()
        lc = post("/api/request/ql/lightcurves", dict(begin=t0, end=t1, ltc=1), "lc_%s.json" % e["flare_id"])
        eph = post("/api/request/ephemeris", dict(start_utc=e["peak"].isoformat(), end_utc=(e["peak"] + dt.timedelta(minutes=1)).isoformat(),
                                                 steps=1), "eph_%s.json" % e["flare_id"])
        p = pulses(lc)
        strong = [q for q in p["pulses"] if q["counts_25_84"] >= 1e5]
        row = dict(e, peak=e["peak"].isoformat(), distance_au=eph["sun_solo_r"][0], earth_sun_solo_deg=eph["earth_sun_solo_angle"][0],
                   n_strong=len(strong), **p)
        table.append(row)
    with open(os.path.join(OUT, "candidates.json"), "w") as fh:
        json.dump(table, fh, indent=1)
    print("| Peak (UTC) | GOES / STIX class | SolO r [AU] | Earth-Sun-SolO [deg] | net 25-50 keV peak [cts/4 s] | pulses | pulses >= 1e5 cts (25-84 keV) | median gap [s] | RCR changes |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in table:
        print("| %s | %s / %s | %.2f | %.0f | %d | %d | %d | %s | %d |" % (
            r["peak"], r["goes"], r["stix_class"], r["distance_au"], r["earth_sun_solo_deg"], r["lc3"],
            r["n_pulses"], r["n_strong"], "%.0f" % r["median_gap_s"] if r["median_gap_s"] else "-", r["rcr_changes"]))


if __name__ == "__main__":
    main()
