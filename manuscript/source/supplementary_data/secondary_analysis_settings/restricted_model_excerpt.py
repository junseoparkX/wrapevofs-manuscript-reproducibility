# Exact model definition recovered from the archived analysis notebook.
# Source: 01_run_restricted_laplace_4chains_GPU_COLAB.ipynb, code cell.
# Imports supplied here for standalone inspection; no analysis is executed.
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist

def restricted_multinomial_laplace_model(X, y=None, n_classes=3):
    _, n_features = X.shape
    n_nonreference = n_classes - 1
    alpha = numpyro.sample(
        "alpha", dist.Normal(0.0, 2.0).expand([n_nonreference]).to_event(1)
    )
    tau_global = numpyro.sample(
        "tau_global", dist.HalfNormal(1.0).expand([n_nonreference]).to_event(1)
    )
    tau_effective = numpyro.deterministic(
        "tau_effective",
        tau_global / jnp.sqrt(jnp.asarray(n_features, dtype=X.dtype)),
    )
    beta_raw = numpyro.sample(
        "beta_raw",
        dist.Laplace(0.0, 1.0).expand([n_nonreference, n_features]).to_event(2),
    )
    betas = numpyro.deterministic(
        "betas", beta_raw * tau_effective[:, None]
    )
    nonreference_logits = alpha[None, :] + X @ betas.T
    logits = jnp.concatenate(
        [jnp.zeros((X.shape[0], 1), dtype=X.dtype), nonreference_logits], axis=1
    )
    numpyro.sample("obs", dist.Categorical(logits=logits), obs=y)
