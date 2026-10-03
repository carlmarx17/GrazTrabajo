"""Read and write the loop-atmosphere file of the FP Fokker-Planck solver (solarFP/FP).

Layout (decoded from FP's python/readatm.py and idl/writeatm.pro, and checked
byte-for-byte against the three example atmospheres shipped with FP on 2026-10-03):
an unformatted Fortran sequential file with two records, little endian.

    record 1: int32  nz, nions, nneutrals
    record 2: float64 zin[nz], tg[nz], bfield[nz], dni[nions][nz]... see below

dni is stored as an (nz, nions) C-ordered array, dnn as (nz, nneutrals), followed by
mion[nions], Zion[nions], Zn[nneutrals], Enion[nneutrals].  Species 0 of dni is the
electron population (mass 511 keV, charge 1), then H+, He+, He++; neutrals are H, He.
Units: zin in cm measured from the photosphere (apex first, decreasing), tg in K,
bfield in G, densities in cm^-3, masses and ionization energies in eV.
"""
from __future__ import annotations

import struct
from dataclasses import dataclass

import numpy as np


@dataclass
class FPAtmosphere:
    zin: np.ndarray      # [cm], apex first
    tg: np.ndarray       # [K]
    bfield: np.ndarray   # [G]
    dni: np.ndarray      # (nz, nions) [cm^-3]; column 0 = electrons
    dnn: np.ndarray      # (nz, nneutrals) [cm^-3]
    mion: np.ndarray     # (nions,) [eV]
    zion: np.ndarray     # (nions,)
    zn: np.ndarray       # (nneutrals,)
    enion: np.ndarray    # (nneutrals,) [eV]

    def __post_init__(self) -> None:
        nz = self.zin.size
        if not (self.tg.size == self.bfield.size == nz == self.dni.shape[0] == self.dnn.shape[0]):
            raise ValueError("all per-depth arrays must have the same length")
        if self.dni.shape[1] != self.mion.size or self.dni.shape[1] != self.zion.size:
            raise ValueError("mion and zion must have one entry per ion species")
        if self.dnn.shape[1] != self.zn.size or self.dnn.shape[1] != self.enion.size:
            raise ValueError("zn and enion must have one entry per neutral species")

    def to_bytes(self) -> bytes:
        nz, ni = self.dni.shape
        nn = self.dnn.shape[1]
        head = np.array([nz, ni, nn], dtype="<i4").tobytes()
        flat = np.concatenate([self.zin, self.tg, self.bfield, self.dni.ravel(), self.dnn.ravel(),
                               self.mion, self.zion, self.zn, self.enion]).astype("<f8").tobytes()
        rec = lambda b: struct.pack("<i", len(b)) + b + struct.pack("<i", len(b))
        return rec(head) + rec(flat)

    def write(self, path: str) -> None:
        with open(path, "wb") as fh:
            fh.write(self.to_bytes())

    @classmethod
    def from_bytes(cls, data: bytes) -> "FPAtmosphere":
        recs, i = [], 0
        while i < len(data):
            n = struct.unpack("<i", data[i:i + 4])[0]
            payload = data[i + 4:i + 4 + n]
            if struct.unpack("<i", data[i + 4 + n:i + 8 + n])[0] != n:
                raise ValueError("corrupt Fortran record markers")
            recs.append(payload)
            i += 8 + n
        if len(recs) != 2:
            raise ValueError("expected 2 records, found %d" % len(recs))
        nz, ni, nn = (int(x) for x in np.frombuffer(recs[0], dtype="<i4"))
        ar = np.frombuffer(recs[1], dtype="<f8")
        if ar.size != nz * (3 + ni + nn) + 2 * ni + 2 * nn:
            raise ValueError("record size does not match the header")
        o = 3 * nz
        dni = ar[o:o + ni * nz].reshape((nz, ni)); o += ni * nz
        dnn = ar[o:o + nn * nz].reshape((nz, nn)); o += nn * nz
        return cls(ar[:nz].copy(), ar[nz:2 * nz].copy(), ar[2 * nz:3 * nz].copy(), dni.copy(), dnn.copy(),
                   ar[o:o + ni].copy(), ar[o + ni:o + 2 * ni].copy(),
                   ar[o + 2 * ni:o + 2 * ni + nn].copy(), ar[o + 2 * ni + nn:o + 2 * ni + 2 * nn].copy())

    @classmethod
    def read(cls, path: str) -> "FPAtmosphere":
        with open(path, "rb") as fh:
            return cls.from_bytes(fh.read())
