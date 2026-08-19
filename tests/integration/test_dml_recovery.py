import numpy as np
import pandas as pd

from causal_inference.core.dml_engine import estimate_price_elasticity

N_OBS = 2000
TRUE_THETA = -0.50
NOISE_SD = 0.5
SEED = 42


def test_dml_recovers_known_theta() -> None:
    """Verifies estimate_price_elasticity recovers a known theta_0 from a synthetic PLR DGP.

    DGP: X1, X2 ~ N(0, 1); D = sin(X1) + 0.5*X2 + nu; Y = theta_0*D + exp(X1/2) + X2 + eps,
    with nu, eps ~ N(0, 0.5^2) independent of each other and of X, and theta_0 = -0.50.

    Tolerance rationale. Under the partialling-out score the PLR estimator is Neyman
    orthogonal, so first-order nuisance estimation error drops out and
    Var(theta_hat) ~= (1/N) * E[eps^2] / E[nu^2]. Here E[eps^2] = E[nu^2] = 0.25, so the
    ratio is exactly 1 and Var(theta_hat) ~= 1/2000 = 5e-4, i.e. an asymptotic standard
    error of ~0.0224. A tolerance of 0.10 is ~4.5 asymptotic SEs.

    The margin is deliberately generous rather than tight because the asymptotic bound is
    not the binding constraint here. This test runs at n_folds=3, n_rep=1 (production uses
    5/5) to stay under ~5s, which inflates finite-sample cross-fitting noise beyond the
    first-order term; and the LightGBM nuisance learners carry fixed hyperparameters chosen
    for the OJ data, so at N=2000 they retain some residual approximation bias against the
    non-linear sin/exp nuisance shapes. If this assertion fails, the likely cause is that
    residual bias, not Monte Carlo error -- widening the tolerance would hide the signal.
    """
    rng = np.random.default_rng(SEED)

    x1 = rng.normal(0.0, 1.0, N_OBS)
    x2 = rng.normal(0.0, 1.0, N_OBS)
    nu = rng.normal(0.0, NOISE_SD, N_OBS)
    eps = rng.normal(0.0, NOISE_SD, N_OBS)

    d = np.sin(x1) + 0.5 * x2 + nu
    y = TRUE_THETA * d + np.exp(x1 / 2) + x2 + eps

    df = pd.DataFrame({"y": y, "d": d, "x1": x1, "x2": x2})

    dml_model = estimate_price_elasticity(
        df=df,
        y_col="y",
        d_col="d",
        x_cols=["x1", "x2"],
        n_folds=3,
        n_rep=1,
        random_seed=SEED,
    )

    theta_hat = float(dml_model.coef[0])
    assert abs(theta_hat - TRUE_THETA) <= 0.10, (
        f"Estimated theta_0 = {theta_hat:.4f} deviates from true {TRUE_THETA} by more than 0.10"
    )


def test_omitted_confounder_biases_upward() -> None:
    """Verifies that omitting a positive common cause biases theta_hat upward as predicted.

    DGP: U ~ N(0, 1); D = 0.8*U + nu; Y = theta_0*D + 0.8*U + eps with theta_0 = 0.0 and
    nu, eps ~ N(0, 0.5^2). U raises both D and Y, so with U omitted the score attributes
    U's outcome contribution to D. Analytically the omitted-variable bias is
    Cov(D, 0.8U)/Var(D) = 0.8*0.8*Var(U) / (0.64*Var(U) + Var(nu)) = 0.64/0.89 ~= 0.72,
    so the omitted fit should sit ~0.72 above the controlled fit (which targets 0.0).
    The 0.30 threshold asserts the sign and a conservative fraction of that magnitude,
    leaving room for cross-fitting noise at n_folds=3 without weakening the directional claim.

    "noise" is drawn independently of U, so the omitted specification conditions on a
    covariate with no confounding content rather than on an empty x_cols set, which the
    DoubleMLData constructor would reject.
    """
    rng = np.random.default_rng(SEED)

    u = rng.normal(0.0, 1.0, N_OBS)
    noise = rng.normal(0.0, 1.0, N_OBS)
    nu = rng.normal(0.0, NOISE_SD, N_OBS)
    eps = rng.normal(0.0, NOISE_SD, N_OBS)

    d = 0.8 * u + nu
    y = 0.0 * d + 0.8 * u + eps

    df = pd.DataFrame({"y": y, "d": d, "u": u, "noise": noise})

    controlled = estimate_price_elasticity(
        df=df[["y", "d", "u"]],
        y_col="y",
        d_col="d",
        x_cols=["u"],
        n_folds=3,
        n_rep=1,
        random_seed=SEED,
    )
    omitted = estimate_price_elasticity(
        df=df[["y", "d", "noise"]],
        y_col="y",
        d_col="d",
        x_cols=["noise"],
        n_folds=3,
        n_rep=1,
        random_seed=SEED,
    )

    theta_controlled = float(controlled.coef[0])
    theta_omitted = float(omitted.coef[0])

    assert theta_omitted > theta_controlled + 0.30, (
        f"Omitted-confounder estimate {theta_omitted:.4f} is not upward-biased relative to "
        f"controlled estimate {theta_controlled:.4f} by the expected margin"
    )
