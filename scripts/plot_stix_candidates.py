"""Small multiples of STIX quick-look light curves for the candidate events (event selection).

Reads the cached quick-look light curves written by scripts/stix_event_search.py helpers
(results/stix_events/cache/lcw_*.json and results/stix_events/inspect_list.json) and writes
docs/figures/fig7_stix_candidates.png.
"""
from __future__ import annotations

import datetime as dt
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results", "stix_events")
OUT = os.path.join(HERE, "..", "docs", "figures", "fig7_stix_candidates.png")
BLUE, ORANGE, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"

plt.rcParams.update({"font.size": 8, "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.5, "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
                     "figure.dpi": 130, "savefig.bbox": "tight"})


def main():
    events = json.load(open(os.path.join(RES, "inspect_list.json")))
    n = len(events)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(13, 2.35 * rows))
    for ax, ev in zip(axes.flat, events):
        lc = json.load(open(os.path.join(RES, "cache", "lcw_%s.json" % ev["peak"].replace(":", ""))))
        t = np.array([dt.datetime.utcfromtimestamp(x) for x in lc["unix_time"]])
        c = {int(k): np.array(v, float) for k, v in lc["light_curves"].items()}
        rcr = np.array(lc["rcr"])
        peak = dt.datetime.fromisoformat(ev["peak"])
        sel = (t > peak - dt.timedelta(minutes=12)) & (t < peak + dt.timedelta(minutes=12))
        pre = slice(0, 60)
        for band, col, lab in ((3, BLUE, "25–50 keV"), (4, ORANGE, "50–84 keV")):
            y = np.clip(c[band] - np.median(c[band][pre]), 1, None)
            ax.semilogy(t[sel], y[sel], color=col, lw=1.1, label=lab)
        for tc in t[1:][np.diff(rcr) != 0]:
            if peak - dt.timedelta(minutes=12) < tc < peak + dt.timedelta(minutes=12):
                ax.axvline(tc, color=INK2, lw=0.6, alpha=0.6)
        ax.set_title("%s  %s  r=%.2f AU, %d° from Earth" % (ev["peak"][:16].replace("T", " "), ev["cls"], ev["r"], ev["ang"]),
                     fontsize=7.5, loc="left", color=INK)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(byminute=range(0, 60, 5)))
        ax.set_ylim(10, None)
    for ax in list(axes.flat)[n:]:
        ax.axis("off")
    axes.flat[0].legend(fontsize=7, loc="upper left", frameon=False)
    fig.text(0.0, -0.01, "STIX quick-look counts per 4 s (summed detectors, pre-flare median subtracted). Gray lines: attenuator / "
             "rate-control changes. * class estimated by STIX for events occulted from Earth.", fontsize=7.5, color=INK2)
    fig.tight_layout()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    fig.savefig(OUT)
    print("written", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
