"""Unit tests for the ideal cylinder projection."""

import math

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
