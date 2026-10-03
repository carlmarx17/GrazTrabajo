import struct

import numpy as np
import pytest

from fp_atmosphere import FPAtmosphere


def _toy(nz=7):
    z = np.linspace(1.3e9, -6e6, nz)
    dni = np.stack([np.linspace(1e9, 1e15, nz), np.linspace(1e9, 1e15, nz)], axis=1)
    dnn = np.linspace(1e2, 1e17, nz).reshape(nz, 1)
    return FPAtmosphere(z, np.linspace(3e6, 5e3, nz), np.linspace(75, 1000, nz), dni, dnn,
                        np.array([5.11e5, 9.38e8]), np.array([1.0, 1.0]), np.array([1.0]), np.array([11.5]))


def test_round_trip_is_exact():
    a = _toy()
    b = FPAtmosphere.from_bytes(a.to_bytes())
    for name in ("zin", "tg", "bfield", "dni", "dnn", "mion", "zion", "zn", "enion"):
        assert np.array_equal(getattr(a, name), getattr(b, name))


def test_layout_two_records_header_then_reals():
    a = _toy(5)
    data = a.to_bytes()
    n1 = struct.unpack("<i", data[:4])[0]
    assert n1 == 12 and np.frombuffer(data[4:16], "<i4").tolist() == [5, 2, 1]
    n2 = struct.unpack("<i", data[20:24])[0]
    assert n2 == 8 * (5 * (3 + 2 + 1) + 2 * 2 + 2 * 1)       # float64 payload
    assert len(data) == 8 + n1 + 8 + n2 and n1 == 12


def test_density_array_is_depth_major():
    # dni is (nz, nions) C-ordered: the first nions values after bfield belong to depth 0
    a = _toy(4)
    flat = np.frombuffer(a.to_bytes()[24:-4], "<f8")
    assert np.array_equal(flat[3 * 4:3 * 4 + 2], a.dni[0])


def test_rejects_inconsistent_sizes_and_corrupt_files():
    a = _toy()
    with pytest.raises(ValueError):
        FPAtmosphere(a.zin[:-1], a.tg, a.bfield, a.dni, a.dnn, a.mion, a.zion, a.zn, a.enion)
    bad = bytearray(a.to_bytes())
    bad[-1] ^= 0xFF
    with pytest.raises(ValueError):
        FPAtmosphere.from_bytes(bytes(bad))
