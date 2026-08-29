#!/usr/bin/env python3
"""
Read ONE electrode out of a 21 GB TUNI .h5 without downloading the file.

HDF5 is a chunked, indexed format. If the web server supports HTTP range
requests, h5py can seek to exactly the bytes it needs and pull only those.
Reading metadata plus ten seconds of one electrode costs tens of megabytes,
not twenty-one gigabytes.

Tested locally: metadata + one electrode from a 288 MB file fetched 9.5 MB (3.3%).

Usage — the URL is the /raw/ link from GIN:

  python stream_h5.py "https://gin.g-node.org/NeuroGroup_TUNI/Comparative_MEA_dataset/raw/master/Data/hPSC_MEA1/hPSC_20517_MEA1_DIV35.h5"

  # the descriptor's own worked example — provable ground truth:
  python stream_h5.py "<url>" --well A3 --electrode 22 --seconds 10

  # just the metadata, costs almost nothing:
  python stream_h5.py "<url>" --info-only

Install once:
  python -m pip install fsspec aiohttp requests h5py numpy scipy matplotlib
"""

import argparse
import sys

import fsspec
import h5py
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import ellip, filtfilt


def as_text(v):
    if isinstance(v, bytes):
        return v.decode("utf-8", errors="replace")
    if isinstance(v, np.ndarray):
        return [as_text(x) for x in v.tolist()]
    if isinstance(v, (list, tuple)):
        return [as_text(x) for x in v]
    return v


def bandpass(trace, fs, low=200.0, high=3000.0):
    nyq = fs / 2.0
    high = min(high, nyq * 0.99)
    b, a = ellip(N=2, rp=0.1, rs=40, Wn=[low / nyq, high / nyq], btype="bandpass")
    return filtfilt(b, a, trace)


def detect_spikes(filtered, threshold_sd=5.0):
    sigma = np.median(np.abs(filtered)) / 0.6745
    thr = threshold_sd * sigma
    below = filtered < -thr
    onsets = np.flatnonzero(np.diff(below.astype(np.int8)) == 1) + 1
    return onsets, thr


def main():
    p = argparse.ArgumentParser(description="Stream one electrode from a remote TUNI .h5")
    p.add_argument("url", help="the /raw/ URL from GIN")
    p.add_argument("--well", default=None)
    p.add_argument("--electrode", default=None)
    p.add_argument("--seconds", type=float, default=10.0)
    p.add_argument("--threshold-sd", type=float, default=5.0)
    p.add_argument("--block-size", type=int, default=4 * 1024 * 1024,
                   help="bytes per range request (default 4 MB)")
    p.add_argument("--info-only", action="store_true",
                   help="metadata only — costs a few MB")
    p.add_argument("--out", default="streamed_spike.png")
    args = p.parse_args()

    print(f"\nOpening remotely (no download):\n  {args.url}\n")

    try:
        handle = fsspec.open(args.url, mode="rb", block_size=args.block_size)
    except Exception as e:
        sys.exit(f"Could not open URL: {e}")

    try:
        with handle as fh:
            try:
                h5 = h5py.File(fh, "r")
            except ValueError as e:
                if "range" in str(e).lower():
                    sys.exit(
                        "\nThis server does not support HTTP range requests, so\n"
                        "streaming is not possible. Fall back to the *_spikes.csv\n"
                        "files, which give per-electrode spike times for a tiny\n"
                        "fraction of the size.\n")
                raise

            # ---- metadata: cheap and the most important part ----
            print("=" * 62)
            print("METADATA  (/DataInfo)")
            print("=" * 62)
            info = h5.get("DataInfo")
            if info is None:
                sys.exit("No /DataInfo group — is this a TUNI file?")
            attrs = {}
            for k in info.attrs:
                attrs[k] = as_text(info.attrs[k])
                print(f"  {k:<26}: {attrs[k]}")
            for name in ("ExcludedWells", "InactiveChannels"):
                if name in info:
                    vals = as_text(info[name][()])
                    n = len(vals) if hasattr(vals, "__len__") else 1
                    print(f"  {name:<26}: {n} entries")
                    print(f"  {'':<26}  {vals}")
                else:
                    print(f"  {name:<26}: (absent)")

            wells = sorted(h5["Data"].keys())
            print(f"\n  wells: {wells}")
            electrodes = sorted(h5["Data"][wells[0]].keys(), key=lambda s: (len(s), s))
            print(f"  electrodes per well: {len(electrodes)}  {electrodes}")
            n_samples = h5["Data"][wells[0]][electrodes[0]].shape[0]
            fs = float(attrs.get("SamplingFrequencyInHz", 12500.0))
            print(f"  samples per electrode: {n_samples}  "
                  f"({n_samples / fs:.1f} s at {fs:.0f} Hz)\n")

            print("  ^ InactiveChannels is the list your whole project rests on.")
            print("    Compare it against the CSV active-electrode counts for this")
            print("    DIV. If they disagree, that disagreement is a finding.\n")

            if args.info_only:
                print(f"  Fetched {getattr(fh.cache, 'total_requested_bytes', 0)/1e6:.1f} MB.\n")
                return

            # ---- one electrode ----
            well = args.well or wells[0]
            if well not in h5["Data"]:
                sys.exit(f"Well {well} not recorded. Available: {wells}")
            elecs = sorted(h5["Data"][well].keys(), key=lambda s: (len(s), s))
            electrode = args.electrode or elecs[0]
            if electrode not in h5["Data"][well]:
                sys.exit(f"Electrode {electrode} not in {well}. Available: {elecs}")

            n = int(min(args.seconds * fs, n_samples))
            print(f"  Reading {n/fs:.0f} s from /Data/{well}/{electrode} ...")
            raw = np.asarray(h5["Data"][well][electrode][:n], dtype=np.float64)
            fetched = getattr(fh.cache, "total_requested_bytes", 0)
    except Exception as e:
        sys.exit(f"\nFailed while reading: {type(e).__name__}: {e}\n")

    t = np.arange(len(raw)) / fs
    filt = bandpass(raw, fs)
    spikes, thr = detect_spikes(filt, args.threshold_sd)

    print()
    print("=" * 62)
    print("RESULT")
    print("=" * 62)
    print(f"  Well {well}, electrode {electrode}, {len(raw)/fs:.1f} s")
    print(f"  Noise threshold : {thr*1e6:.1f} uV ({args.threshold_sd} x robust SD)")
    print(f"  Spikes detected : {len(spikes)}")
    print(f"  Firing rate     : {len(spikes)/(len(raw)/fs):.2f} Hz")
    print(f"  Bytes fetched   : {fetched/1e6:.1f} MB  (file is ~21000 MB)")
    print()

    fig, axes = plt.subplots(3, 1, figsize=(12, 8))
    axes[0].plot(t, raw * 1e6, linewidth=0.4)
    axes[0].set_title(f"Raw — {well}/{electrode} (streamed)")
    axes[1].plot(t, filt * 1e6, linewidth=0.4)
    axes[1].axhline(-thr * 1e6, linestyle="--", linewidth=0.8)
    if len(spikes):
        axes[1].plot(spikes / fs, filt[spikes] * 1e6, "v", markersize=4)
    axes[1].set_title(f"Bandpass 200–3000 Hz — {len(spikes)} spikes")
    if len(spikes):
        c = spikes[0]
        half = int(0.002 * fs)
        lo, hi = max(0, c - half), min(len(filt), c + half)
        axes[2].plot((np.arange(lo, hi) - c) / fs * 1000, filt[lo:hi] * 1e6, linewidth=1.2)
        axes[2].set_title("First spike, ±2 ms")
        axes[2].set_xlabel("ms")
    else:
        axes[2].text(0.5, 0.5, "no spikes detected", ha="center", va="center")
    for ax in axes[:2]:
        ax.set_xlabel("time (s)")
        ax.set_ylabel("µV")
    fig.tight_layout()
    fig.savefig(args.out, dpi=150)
    print(f"  Figure written to {args.out}\n")


if __name__ == "__main__":
    main()
