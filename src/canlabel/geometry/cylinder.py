"""理想円筒の射影: 水平位置 <-> 表面角。

円筒は見かけの半径 ``R``(画素)の正射影で見る。見かけの中心から水平距離 ``x`` の
点は、表面上の角度 ``alpha`` にあり、``x = R * sin(alpha)`` が成り立つ。
``alpha = 0`` はカメラに正対する位置。
"""

import numpy as np

# これより狭い浮動小数点dtypeの入力では、半径をそのdtypeに丸めて比較する。
_FLOAT64_BITS = np.finfo(np.float64).bits


def _check_radius(radius: float) -> float:
    r = float(radius)
    if not np.isfinite(r) or r <= 0.0:
        raise ValueError(f"radius must be a finite value > 0, got {radius!r}")
    return r


def _effective_radius(x: float | np.ndarray, r: float) -> float:
    """``x`` が float64 より狭い浮動小数点dtypeのとき、``r`` を ``x`` の精度に丸める。

    それ以外の入力(float64、longdouble、整数、Pythonスカラー)では ``r`` をそのまま返す。
    """
    dtype = np.asarray(x).dtype
    if not np.issubdtype(dtype, np.floating) or np.finfo(dtype).bits >= _FLOAT64_BITS:
        return r
    with np.errstate(over="ignore", under="ignore"):
        r_eff = float(dtype.type(r))
    if not np.isfinite(r_eff) or r_eff <= 0.0:
        raise ValueError(
            f"radius {r!r} を {dtype} に丸めた値 r_eff = {r_eff!r} が、正の有限値になりません"
        )
    return r_eff


def _to_float64(values: float | np.ndarray, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} must be finite (no NaN or inf)")
    return arr


def _finish(result: np.ndarray, values: float | np.ndarray) -> float | np.ndarray:
    # NumPyのufuncは0次元配列をNumPyスカラーにしてしまうので、先に配列へ戻す。
    out = np.asarray(result, dtype=np.float64)
    assert out.shape == np.shape(values)
    assert out.dtype == np.float64
    if isinstance(values, np.ndarray):
        return out
    return float(out)


def x_to_alpha(x: float | np.ndarray, radius: float) -> float | np.ndarray:
    """水平位置を円筒の表面角に変換する: ``alpha = arcsin(x / R)``。

    Args:
        x: 円筒の見かけの中心からの水平距離(画素)。Pythonスカラー、NumPyスカラー、
            または0次元を含む任意shapeのndarray(任意の実数dtype。計算はfloat64)。
            ``|x| <= radius`` を満たすこと。
        radius: 見かけの半径 ``R``(画素)。``> 0`` の有限スカラー。

    境界の扱い:
        範囲判定は ``x`` のdtypeの精度で行う。float64より狭い浮動小数点dtype
        (float32など)では、まず ``radius`` をそのdtypeに丸めて
        ``R_eff = dtype(radius)`` を求め、判定 ``|x| <= R_eff`` と除算 ``x / R_eff`` の
        両方に ``R_eff`` を使う。このため ``R``(例: 0.1)がそのdtypeで正確に表せなくても、
        ``x = dtype(R)`` は受理されて厳密に ``pi/2`` を返す(``-R`` は ``-pi/2``)。
        許容する誤差は、そのdtypeでの ``radius`` の丸め誤差1回分だけである
        (float32で相対約6e-8)。結果は ``R`` をそのまま使った場合と、その程度だけずれる。
        これは範囲内への丸め(clip)ではない。``R_eff`` を超える値は、これまでどおり
        ``ValueError`` になる。float64、longdouble、整数、Pythonスカラーの入力は
        ``radius`` をそのまま使う(半径 ``1.0`` に対して ``1.0 + 1e-9`` は範囲外)。

    Returns:
        ``[-pi/2, pi/2]`` の範囲のラジアン角。常にfloat64。スカラー入力にはPythonの
        ``float``、ndarray入力には ``x`` と同じshapeのfloat64のndarrayを返す
        (0次元ndarrayは0次元ndarrayのまま)。

    Raises:
        ValueError: ``radius`` が有限でない、または ``<= 0`` の場合。``x`` にNaN/infが
            含まれる場合。``|x| > R_eff`` の値がある場合(上記参照)。``x`` のdtypeが
            より狭い浮動小数点で、``radius`` を丸めた結果が0またはinfになる場合。
            値はclipしない。
    """
    r_eff = _effective_radius(x, _check_radius(radius))
    arr = _to_float64(x, "x")
    if arr.size and np.max(np.abs(arr)) > r_eff:
        raise ValueError(
            f"|x| は実効半径 r_eff 以下でなければなりません: max |x| = {np.max(np.abs(arr))}, "
            f"r_eff = {r_eff}"
        )
    return _finish(np.arcsin(arr / r_eff), x)


def alpha_to_x(alpha: float | np.ndarray, radius: float) -> float | np.ndarray:
    """円筒の表面角を水平位置に変換する: ``x = R * sin(alpha)``。

    Args:
        alpha: 表面角(ラジアン)。スカラー、または0次元を含む任意shapeのndarray
            (任意の実数dtype。float64に変換する)。:func:`x_to_alpha` との往復が
            保証されるのは ``|alpha| <= pi/2`` のときだけ。
        radius: 見かけの半径 ``R``(画素)。``> 0`` の有限スカラー。

    Returns:
        見かけの中心からの水平距離(画素)。範囲は ``[-R, R]``。スカラー入力には
        Pythonの ``float``、ndarray入力には ``alpha`` と同じshapeのfloat64のndarray
        を返す(0次元ndarrayは0次元ndarrayのまま)。

    Raises:
        ValueError: ``radius`` が有限でない、または ``<= 0`` の場合。``alpha`` に
            NaN/infが含まれる場合。
    """
    r = _check_radius(radius)
    arr = _to_float64(alpha, "alpha")
    return _finish(r * np.sin(arr), alpha)
