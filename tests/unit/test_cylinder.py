"""Unit tests for the ideal cylinder projection."""

import math
from typing import cast

import numpy as np
import pytest

from canlabel.geometry.cylinder import alpha_to_x, x_to_alpha

RADII = [1.0, 250.0]


@pytest.mark.parametrize("r", RADII)
def test_x_to_alpha_boundaries(r: float) -> None:
    assert x_to_alpha(0.0, r) == 0.0
    assert x_to_alpha(r, r) == pytest.approx(math.pi / 2)
    assert x_to_alpha(-r, r) == pytest.approx(-math.pi / 2)


@pytest.mark.parametrize("r", RADII)
def test_x_to_alpha_known_values(r: float) -> None:
    assert x_to_alpha(r / 2, r) == pytest.approx(math.pi / 6)
    assert x_to_alpha(-r / 2, r) == pytest.approx(-math.pi / 6)
    assert x_to_alpha(r * math.sqrt(2) / 2, r) == pytest.approx(math.pi / 4)


@pytest.mark.parametrize("r", RADII)
def test_alpha_to_x_known_values(r: float) -> None:
    assert alpha_to_x(0.0, r) == 0.0
    assert alpha_to_x(math.pi / 2, r) == pytest.approx(r)
    assert alpha_to_x(-math.pi / 2, r) == pytest.approx(-r)
    assert alpha_to_x(math.pi / 6, r) == pytest.approx(r / 2)


@pytest.mark.parametrize("r", RADII)
def test_round_trip_arrays(r: float) -> None:
    x = np.linspace(-r, r, 1001)
    np.testing.assert_allclose(alpha_to_x(x_to_alpha(x, r), r), x, rtol=1e-12, atol=1e-12)
    a = np.linspace(-math.pi / 2, math.pi / 2, 1001)
    np.testing.assert_allclose(x_to_alpha(alpha_to_x(a, r), r), a, rtol=1e-7, atol=1e-7)


def test_round_trip_near_edge() -> None:
    r = 100.0
    x = np.array([-r, -r * (1 - 1e-9), r * (1 - 1e-9), r])
    np.testing.assert_allclose(alpha_to_x(x_to_alpha(x, r), r), x, rtol=1e-12, atol=1e-12)


def test_scalar_returns_float() -> None:
    assert type(x_to_alpha(1.0, 2.0)) is float
    assert type(alpha_to_x(0.3, 2.0)) is float
    assert type(x_to_alpha(1, 2)) is float


@pytest.mark.parametrize("shape", [(5,), (3, 4)])
def test_array_shape_and_dtype(shape: tuple[int, ...]) -> None:
    x = np.zeros(shape, dtype=np.float32)
    for out in (x_to_alpha(x, 1.0), alpha_to_x(x, 1.0)):
        assert isinstance(out, np.ndarray)
        assert out.shape == shape
        assert out.dtype == np.float64


def test_one_element_array_stays_array() -> None:
    assert isinstance(x_to_alpha(np.array([0.5]), 1.0), np.ndarray)


def test_zero_dim_array_stays_array() -> None:
    x = np.array(0.5)
    for out in (x_to_alpha(x, 1.0), alpha_to_x(x, 1.0)):
        assert isinstance(out, np.ndarray)
        assert out.shape == ()
        assert out.dtype == np.float64
    assert x_to_alpha(x, 1.0) == pytest.approx(math.pi / 6)


def test_numpy_scalar_returns_float() -> None:
    assert type(x_to_alpha(np.float64(0.5), 1.0)) is float
    assert type(alpha_to_x(np.float64(0.5), 1.0)) is float


def test_integer_array() -> None:
    out = x_to_alpha(np.array([-2, 0, 2]), 2)
    np.testing.assert_allclose(out, [-math.pi / 2, 0.0, math.pi / 2])


def test_input_not_modified() -> None:
    x = np.array([-1.0, 0.5, 1.0])
    orig = x.copy()
    x_to_alpha(x, 1.0)
    alpha_to_x(x, 1.0)
    np.testing.assert_array_equal(x, orig)


@pytest.mark.parametrize("x", [1.5, -1.5, 1.0 + 1e-9])
def test_out_of_range_scalar_raises(x: float) -> None:
    with pytest.raises(ValueError):
        x_to_alpha(x, 1.0)


def test_out_of_range_partial_array_raises() -> None:
    with pytest.raises(ValueError):
        x_to_alpha(np.array([0.0, 0.5, 1.1]), 1.0)


@pytest.mark.parametrize("r", [0.0, -1.0, math.nan, math.inf])
def test_invalid_radius_raises(r: float) -> None:
    with pytest.raises(ValueError):
        x_to_alpha(0.0, r)
    with pytest.raises(ValueError):
        alpha_to_x(0.0, r)


@pytest.mark.parametrize("v", [math.nan, math.inf])
def test_non_finite_input_raises(v: float) -> None:
    with pytest.raises(ValueError):
        x_to_alpha(v, 1.0)
    with pytest.raises(ValueError):
        alpha_to_x(np.array([0.0, v]), 1.0)


@pytest.mark.parametrize("r", [0.1, 0.3, 1e-3, 1.0, 123.456])
def test_x_to_alpha_float32_boundary(r: float) -> None:
    x = np.array([r, -r], dtype=np.float32)
    out = x_to_alpha(x, r)
    assert isinstance(out, np.ndarray)
    assert out.dtype == np.float64
    assert not np.any(np.isnan(out))
    np.testing.assert_allclose(out, [math.pi / 2, -math.pi / 2], atol=1e-6)


@pytest.mark.parametrize("r", [0.1, 0.3, 1.0, 12.3])
def test_x_to_alpha_float16_boundary(r: float) -> None:
    x = np.array([r, -r], dtype=np.float16)
    out = x_to_alpha(x, r)
    assert isinstance(out, np.ndarray)
    assert out.dtype == np.float64
    np.testing.assert_allclose(out, [math.pi / 2, -math.pi / 2], atol=1e-6)


def test_x_to_alpha_float32_scalar_boundary() -> None:
    out = x_to_alpha(cast(float, np.float32(0.1)), 0.1)
    assert isinstance(out, float)
    assert out == pytest.approx(math.pi / 2, abs=1e-6)


@pytest.mark.parametrize("sign", [1.0, -1.0])
def test_x_to_alpha_float32_beyond_rounding_raises(sign: float) -> None:
    r = 0.1
    over = np.nextafter(np.float32(r), np.float32(np.inf))
    with pytest.raises(ValueError):
        x_to_alpha(np.array([sign * over], dtype=np.float32), r)
    with pytest.raises(ValueError):
        x_to_alpha(np.array([sign * 0.1001], dtype=np.float32), r)
    with pytest.raises(ValueError):
        x_to_alpha(np.array([sign * r * (1 + 1e-6)], dtype=np.float64), r)


def test_x_to_alpha_float64_unchanged() -> None:
    with pytest.raises(ValueError):
        x_to_alpha(1.0 + 1e-9, 1.0)
    with pytest.raises(ValueError):
        x_to_alpha(0.1000000001, 0.1)
    assert x_to_alpha(np.float64(0.1), 0.1) == pytest.approx(math.pi / 2)


def test_x_to_alpha_float32_interior_matches_float64() -> None:
    x32 = np.linspace(-0.09, 0.09, 11, dtype=np.float32)
    got = x_to_alpha(x32, 0.1)
    expected = x_to_alpha(x32.astype(np.float64), 0.1)
    np.testing.assert_allclose(got, expected, rtol=1e-6)


def test_x_to_alpha_float32_degenerate_radius_raises() -> None:
    with pytest.raises(ValueError):
        x_to_alpha(np.array([0.0], dtype=np.float32), 1e-50)
    with pytest.raises(ValueError):
        x_to_alpha(np.array([0.0], dtype=np.float16), 1e6)
