# Exact archived full-model definition; no fitting is executed.
import jax.numpy as jnp
import numpyro
import numpyro.distributions as dist

def multinomial_shrinkage_model(X, y=None, n_classes=3):
    n_observations, n_features = X.shape
    n_nonreference = n_classes - 1

    alpha = numpyro.sample(
        "alpha",
        dist.Normal(0.0, 2.0).expand([n_nonreference]).to_event(1),
    )

    tau_global = numpyro.sample(
        "tau_global",
        dist.HalfNormal(1.0).expand([n_nonreference]).to_event(1),
    )

    beta_raw = numpyro.sample(
        "beta_raw",
        dist.Normal(0.0, 1.0)
        .expand([n_nonreference, n_features])
        .to_event(2),
    )

    tau_effective = tau_global / jnp.sqrt(jnp.asarray(n_features, dtype=X.dtype))
    betas = beta_raw * tau_effective[:, None]

    nonreference_logits = alpha[None, :] + X @ betas.T
    reference_logits = jnp.zeros((n_observations, 1), dtype=X.dtype)
    logits = jnp.concatenate([reference_logits, nonreference_logits], axis=1)

    with numpyro.plate("observations", n_observations):
        numpyro.sample("obs", dist.Categorical(logits=logits), obs=y)
