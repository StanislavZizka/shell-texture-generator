from __future__ import annotations

import numpy as np

from evaluation.metrics_stripes import stripe_blob_penalty


def test_stripe_blob_penalty_is_lower_for_clean_stripes_than_for_speckle():
    x = np.linspace(0.0, 4.0 * np.pi, 128, dtype=np.float64)
    stripes = np.tile(0.5 + 0.5 * np.sin(x), (128, 1))

    speckle = stripes.copy()
    speckle[20:24, 30:34] = 1.0
    speckle[80:84, 90:94] = 0.0

    assert stripe_blob_penalty(stripes) < stripe_blob_penalty(speckle)
