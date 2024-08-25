import numpy as np
import pandas as pd
import streamlit as st


def sample(array: np.ndarray | pd.Series, num_samples: int = 1) -> np.ndarray:
    """
    Randomly sample values from an array.
    """
    if isinstance(array, pd.Series):
        array = array.to_numpy()

    return np.random.default_rng().choice(array, size=num_samples)

def simulate_payoffs(hist_returns: pd.Series,
                     num_scenarios: int,
                     start_value: float,
                     mean: float,
                     volatility: float) -> np.ndarray:
    """
    Simulate next period portfolio increase assuming returns are i.i.d.
    """
    returns = sample(array=hist_returns, num_samples=num_scenarios)

    # scale to mean 0, variance 1
    returns -= returns.mean(keepdims=True)
    returns /= returns.std(keepdims=True)

    # adjust to target mean and volatility
    returns *= volatility
    returns += mean

    # make sure that there are no returns lower than -100%
    # i.e. we cannot lose more than we had
    returns = np.clip(returns, a_min=-1.0, a_max=None)

    return start_value * returns

def simulate_portfolio_values(hist_values: pd.Series,
                              start_value: float,
                              years_before_ret: int,
                              years_after_ret: int,
                              yearly_installment: float,
                              yearly_withdrawls: float,
                              num_scenarios: int,
                              mean: float,
                              volatility: float) -> tuple[pd.DataFrame, dict[str, list[float]]]:
    """
    Simulate portfolio value V(t).
    If t <= years_before_ret, then V(t) = V(t-1) * (1 + r(t)) + yearly_installment.
    If t > years_before_ret, then V(t-1) * (1 + r(t)) - yearly_withdrawl.
    In words, we invest fixed amount each year before retirement.
    Once retired, we only withdraw from our account (but still earn interest).
    """
    num_years = years_before_ret + years_after_ret
    portfolio_values = np.zeros((num_years + 1, num_scenarios))
    portfolio_values[0, :] = start_value

    metadata = {
        "Invested per year": [0.0],
        "Mean earnings per year": [0.0],
        "Median earnings per year": [0.0],
        "Withdrawn per year": [0.0],
    }

    for t in range(1, num_years + 1):
        portfolio_growth = simulate_payoffs(hist_returns=hist_values,
                                                   num_scenarios=num_scenarios,
                                                   start_value=portfolio_values[t - 1, :],
                                                   mean=mean,
                                                   volatility=volatility)

        metadata["Mean earnings per year"].append(np.mean(portfolio_growth))
        metadata["Median earnings per year"].append(np.median(portfolio_growth))

        portfolio_values[t, :] = portfolio_values[t - 1, :] + portfolio_growth

        if t <= years_before_ret:
            portfolio_values[t, :] += yearly_installment
            metadata["Invested per year"].append(yearly_installment)
            metadata["Withdrawn per year"].append(0.0)
        else:
            portfolio_values[t, :] -= yearly_withdrawls
            metadata["Invested per year"].append(0.0)
            metadata["Withdrawn per year"].append(yearly_withdrawls)

    portfolio_values = pd.DataFrame(portfolio_values)
    portfolio_values.index.name = "Year"

    return portfolio_values, metadata

@st.cache_data
def simulate_and_stats(hist_values: pd.Series,
                       start_value: float,
                       years_before_ret: int,
                       years_after_ret: int,
                       yearly_installment: float,
                       yearly_withdrawls: float,
                       num_scenarios: int,
                       mean: float,
                       volatility: float) -> pd.DataFrame:
    """
    Simulate portfolio values and compute statistics on them.
    """
    scenarios, metadata = simulate_portfolio_values(hist_values=hist_values,
                                                    start_value=start_value,
                                                    years_before_ret=years_before_ret,
                                                    years_after_ret=years_after_ret,
                                                    yearly_installment=yearly_installment,
                                                    yearly_withdrawls=yearly_withdrawls,
                                                    num_scenarios=num_scenarios,
                                                    mean=mean,
                                                    volatility=volatility)

    stats = pd.DataFrame({
        "Mean": scenarios.mean(axis=1),
        "Median": scenarios.median(axis=1),
        "Percentile 5": scenarios.quantile(0.05, axis=1),
        "Percentile 25": scenarios.quantile(0.25, axis=1),
        "Percentile 75": scenarios.quantile(0.75, axis=1),
        "Percentile 95": scenarios.quantile(0.95, axis=1),
        "Total invested": np.cumsum(metadata["Invested per year"]),
        "Total withdrawn": np.cumsum(metadata["Withdrawn per year"]),
        "Total mean return": np.cumsum(metadata["Mean earnings per year"]),
        "Total median return": np.cumsum(metadata["Median earnings per year"]),
        **metadata,
    })

    return stats
