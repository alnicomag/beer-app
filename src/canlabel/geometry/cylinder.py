"""Ideal cylinder projection: horizontal position <-> surface angle.

The cylinder is viewed orthographically with apparent radius ``R`` (pixels).
A point at horizontal distance ``x`` from the apparent center lies at angle
``alpha`` on the surface, where ``x = R * sin(alpha)``. ``alpha = 0`` faces
the camera.
"""

import numpy as np


def _check_radius(radius: float) -> float:
    r = float(radius)
    if not np.isfinite(r) or r <= 0.0:
        raise ValueError(f"radius must be a finite value > 0, got {radius!r}")
    return r


def _to_float64(values: float | np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite (no NaN or inf)")
    return arr


def _finish(result: np.ndarray, values: float | np.ndarray) -> float | np.ndarray:
    # NumPy ufuncs turn 0-d arrays into NumPy scalars, so restore the array first.
    out = np.asarray(result, dtype=np.float64)
    assert out.shape == np.shape(values)
    assert out.dtype == np.float64
    if isinstance(values, np.ndarray):
        return out
    return float(out)


def x_to_alpha(x: float | np.ndarray, radius: float) -> float | np.ndarray:
    """Convert horizontal position to cylinder surface angle: ``alpha = arcsin(x / R)``.

    Args:
        x: Horizontal distance from the apparent cylinder center, in pixels.
            A Python/NumPy scalar or an ndarray of any shape, including 0-d
            (any real dtype; converted to float64). Must satisfy ``|x| <= radius``.
        radius: Apparent radius ``R`` in pixels. Finite scalar ``> 0``.

    Returns:
        Angle in radians, within ``[-pi/2, pi/2]``. A Python ``float`` for scalar
        input; for ndarray input, a float64 ndarray with the same shape as ``x``
        (a 0-d ndarray stays a 0-d ndarray).

    Raises:
        ValueError: If ``radius`` is not finite or ``<= 0``, if ``x`` contains NaN/inf,
            or if any ``|x| > radius``. Values are never clipped.
    """
    r = _check_radius(radius)
    arr = _to_float64(x, "x")
    if arr.size and np.max(np.abs(arr)) > r:
        raise ValueError(f"|x| must be <= radius: max |x| = {np.max(np.abs(arr))}, radius = {r}")
    return _finish(np.arcsin(arr / r), x)


def alpha_to_x(alpha: float | np.ndarray, radius: float) -> float | np.ndarray:
    """Convert cylinder surface angle to horizontal position: ``x = R * sin(alpha)``.

    Args:
        alpha: Surface angle in radians. Scalar or ndarray of any shape, including
            0-d (any real dtype; converted to float64). Round-tripping with :func:`x_to_alpha`
            is guaranteed only for ``|alpha| <= pi/2``.
        radius: Apparent radius ``R`` in pixels. Finite scalar ``> 0``.

    Returns:
        Horizontal distance from the apparent center in pixels, within ``[-R, R]``.
        A Python ``float`` for scalar input; for ndarray input, a float64 ndarray
        with the same shape as ``alpha`` (a 0-d ndarray stays a 0-d ndarray).

    Raises:
        ValueError: If ``radius`` is not finite or ``<= 0``, or ``alpha`` contains NaN/inf.
    """
    r = _check_radius(radius)
    arr = _to_float64(alpha, "alpha")
    return _finish(r * np.sin(arr), alpha)
