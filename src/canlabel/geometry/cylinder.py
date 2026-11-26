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


def _effective_radius(x: float | np.ndarray, r: float) -> float:
    """Round ``r`` to the precision of ``x`` when ``x`` is a float dtype narrower than float64.

    Other inputs (float64, longdouble, integers, Python scalars) leave ``r`` unchanged.
    """
    dtype = np.asarray(x).dtype
    if not np.issubdtype(dtype, np.floating) or np.finfo(dtype).bits >= 64:
        return r
    with np.errstate(over="ignore", under="ignore"):
        r_eff = float(dtype.type(r))
    if not np.isfinite(r_eff) or r_eff <= 0.0:
        raise ValueError(f"radius {r!r} is not representable as a positive finite {dtype}")
    return r_eff


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
            (any real dtype; computed in float64). Must satisfy ``|x| <= radius``.
        radius: Apparent radius ``R`` in pixels. Finite scalar ``> 0``.

    Boundary handling:
        The range check is done at the precision of ``x``'s dtype. For a float
        dtype narrower than float64 (e.g. float32), ``radius`` is first rounded to
        that dtype, ``R_eff = dtype(radius)``, and both the check ``|x| <= R_eff``
        and the division ``x / R_eff`` use ``R_eff``. So ``x = dtype(R)`` is
        accepted and gives exactly ``pi/2`` (``-R`` gives ``-pi/2``), even when
        ``R`` (e.g. 0.1) is not exactly representable in that dtype. The only
        tolerance is the rounding error of ``radius`` in that dtype (about 6e-8
        relative for float32); results differ from using ``R`` directly by about
        that much. This is not clipping: any value above ``R_eff`` still raises.
        float64, longdouble, integer and Python scalar inputs use ``radius`` as is
        (``1.0 + 1e-9`` is out of range for radius ``1.0``).

    Returns:
        Angle in radians, within ``[-pi/2, pi/2]``, always float64. A Python ``float`` for scalar
        input; for ndarray input, a float64 ndarray with the same shape as ``x``
        (a 0-d ndarray stays a 0-d ndarray).

    Raises:
        ValueError: If ``radius`` is not finite or ``<= 0``, if ``x`` contains NaN/inf,
            if any ``|x| > R_eff`` (see above), or if ``radius`` rounded to a narrower
            float dtype of ``x`` becomes 0 or inf. Values are never clipped.
    """
    r = _effective_radius(x, _check_radius(radius))
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
