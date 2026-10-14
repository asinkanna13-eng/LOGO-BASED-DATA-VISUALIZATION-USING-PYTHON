import math

import numpy as np # pyright: ignore[reportMissingImports]
import pandas as pd # pyright: ignore[reportMissingModuleSource]


def calculate_metrics(values):
    numeric = np.asarray(values, dtype=float)
    if numeric.size == 0:
        raise ValueError("The dataset has no numeric values.")
    minimum, maximum = float(numeric.min()), float(numeric.max())
    span = maximum - minimum
    normalized = np.zeros_like(numeric) if span == 0 else (numeric - minimum) / span
    percentage_change = ((numeric[-1] - numeric[0]) / abs(numeric[0]) * 100) if numeric[0] else 0.0
    periods = max(numeric.size - 1, 1)
    cagr = ((numeric[-1] / numeric[0]) ** (1 / periods) - 1) * 100 if numeric[0] > 0 and numeric[-1] >= 0 else 0.0
    differences = np.diff(numeric)
    correlation = float(np.corrcoef(np.arange(numeric.size), numeric)[0, 1]) if numeric.size > 1 and np.std(numeric) else 0.0
    return {
        "count": int(numeric.size),
        "mean": float(np.mean(numeric)),
        "median": float(np.median(numeric)),
        "std_dev": float(np.std(numeric)),
        "minimum": minimum,
        "maximum": maximum,
        "sum": float(np.sum(numeric)),
        "percentage_change": float(percentage_change),
        "growth_rate": float(np.mean(differences / np.abs(numeric[:-1])) * 100) if differences.size and np.all(numeric[:-1] != 0) else 0.0,
        "cagr": float(cagr),
        "alpha": float(np.mean(numeric) - np.median(numeric)),
        "beta": float(np.var(numeric) / (np.var(np.arange(numeric.size)) or 1)),
        "correlation": correlation,
        "rho": correlation,
        "lambda": float(np.mean(normalized)),
        "normalized": normalized.tolist(),
    }


def geometric_points(count, radius=1.0):
    angles = np.linspace(0, 2 * math.pi, max(count, 1), endpoint=False)
    return [(radius * math.cos(theta), radius * math.sin(theta)) for theta in angles]