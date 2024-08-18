import numpy as np
import pandas as pd
import streamlit as st

path = "utils/assets/real_sp_yearly_returns.csv"
hist_returns = pd.read_csv(path, index_col="Date")["0"]


def sample(array: np.ndarray | pd.Series, num_samples: int = 1) -> np.array:
    if isinstance(array, pd.Series):
        array = array.to_numpy()

    return np.random.default_rng().choice(array, size=num_samples)

def sim_payoff_bootstrapped(hist_returns: pd.Series,
                            num_scenarios: int,
                            start_value: float) -> np.ndarray:
    """
    Simulate next period portfolio increase assuming returns are i.i.d.
    """
    returns = sample(array=hist_returns, num_samples=num_scenarios)
    return start_value * returns

def simulate(start_value: float, years_before_ret: int, years_after_ret: int,
             yearly_installment: float, yearly_withdrawls: float,
             num_scenarios: int, start_date: str) -> pd.DataFrame:
    num_years = years_before_ret + years_after_ret
    portfolio_values = np.zeros((num_years + 1, num_scenarios))
    portfolio_values[0, :] = start_value

    hist_values = hist_returns.loc[start_date:]

    metadata = {
        "Invested per year": [0.0],
        "Mean earnings per year": [0.0],
        "Median earnings per year": [0.0],
        "Withdrawn per year": [0.0],
    }

    for t in range(1, num_years + 1):
        portfolio_growth = sim_payoff_bootstrapped(hist_values,
                                                   num_scenarios,
                                                   portfolio_values[t - 1, :])

        metadata["Mean earnings per year"].append(np.mean(portfolio_growth))
        metadata["Median earnings per year"].append(np.median(portfolio_growth))

        portfolio_values[t, :] = portfolio_values[t - 1, :] + portfolio_growth

        if t < years_before_ret:
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
def compute_portfolio_stats(start_value: float, years_before_ret: int, years_after_ret: int,
                            yearly_installment: float, yearly_withdrawls: float,
                            num_scenarios: int, start_date: str) -> pd.DataFrame:

    scenarios, metadata = simulate(start_value=start_value,
                                   years_before_ret=years_before_ret,
                                   years_after_ret=years_after_ret,
                                   yearly_installment=yearly_installment,
                                   yearly_withdrawls=yearly_withdrawls,
                                   num_scenarios=num_scenarios,
                                   start_date=start_date)

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
