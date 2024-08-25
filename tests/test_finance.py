from dataclasses import dataclass

import pandas as pd
import pytest
from pandas.api.types import is_numeric_dtype

from tools.finance import simulate_and_stats, simulate_payoffs, simulate_portfolio_values

sample_series = pd.Series({
        pd.to_datetime("2013-12-31"): 0.25,
        pd.to_datetime("2014-12-31"): 0.42,
        pd.to_datetime("2015-12-31"): -0.25,
        pd.to_datetime("2016-12-31"): -0.33,
        pd.to_datetime("2017-12-31"): 0.02,
    })

@dataclass
class TestParameters:
    start_value: float = 42_000
    num_scenarios: int = 100
    years_before_retirement: int = 30
    years_after_retiirement: int = 20
    yearly_installment: float = 20_000
    yearly_withdrawl: float = 50_000

parameters = TestParameters()

@pytest.mark.parametrize("mean", [sample_series.mean(), 0.05])
@pytest.mark.parametrize("volatility", [sample_series.std(), 0.24])
def test_sim_payoff(mean: float, volatility: float) -> None:
    simulated_payoff = simulate_payoffs(hist_returns=sample_series,
                                               num_scenarios=parameters.num_scenarios,
                                               start_value=parameters.start_value,
                                               mean=mean,
                                               volatility=volatility)

    assert simulated_payoff.mean() == pytest.approx(mean * parameters.start_value)
    assert simulated_payoff.std() == pytest.approx(volatility * parameters.start_value)
    assert len(simulated_payoff) == parameters.num_scenarios


@pytest.mark.parametrize("mean", [sample_series.mean(), 0.05])
@pytest.mark.parametrize("volatility", [sample_series.std(), 0.24])
def test_simulate(mean: float, volatility: float) -> None:
    scenarios, _ = simulate_portfolio_values(hist_values=sample_series,
                            start_value=parameters.start_value,
                            years_before_ret=parameters.years_before_retirement,
                            years_after_ret=parameters.years_after_retiirement,
                            yearly_installment=parameters.yearly_installment,
                            yearly_withdrawls=parameters.yearly_withdrawl,
                            num_scenarios=parameters.num_scenarios,
                            mean=mean,
                            volatility=volatility)

    # before retirement portfolio value V(t) is defined as
    # V(t) = V(t-1) * (1 + r(t)) + yearly_installment
    # hence, r(t) = (V(t) - yearly_installment) / V(t-1) - 1

    v_t = scenarios.iloc[:parameters.years_before_retirement]

    # test that returns in the first years_before_ret years are correct (=mean)
    yearly_returns = v_t.sub(parameters.yearly_installment).div(v_t.shift(1)).sub(1)

    assert yearly_returns.mean(axis=1).mean() == pytest.approx(mean)
    assert yearly_returns.std(axis=1).mean() == pytest.approx(volatility, rel=0.01)

    # after retirement portfolio value V(t) is defined as
    # V(t) = V(t-1) * (1 + r(t)) - yearly_withdrawl
    # hence, r(t) = (V(t) + yearly_withdrawl) / V(t-1) - 1

    v_t = scenarios.iloc[parameters.years_before_retirement:]
    yearly_returns = v_t.add(parameters.yearly_withdrawl).div(v_t.shift(1)).sub(1)

    assert yearly_returns.mean(axis=1).mean() == pytest.approx(mean)
    assert yearly_returns.std(axis=1).mean() == pytest.approx(volatility, rel=0.01)

@pytest.mark.parametrize("mean", [sample_series.mean(), 0.05])
@pytest.mark.parametrize("volatility", [sample_series.std(), 0.24])
def test_simulate_and_stats(mean: float, volatility: float) -> None:
    stats = simulate_and_stats(hist_values=sample_series,
                               start_value=parameters.start_value,
                               years_before_ret=parameters.years_before_retirement,
                               years_after_ret=parameters.years_after_retiirement,
                               yearly_installment=parameters.yearly_installment,
                               yearly_withdrawls=parameters.yearly_withdrawl,
                               num_scenarios=parameters.num_scenarios,
                               mean=mean,
                               volatility=volatility)

    assert all(is_numeric_dtype(dtype) for dtype in stats.dtypes)
    assert stats.isna().sum().sum() == 0
