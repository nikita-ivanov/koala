from dataclasses import dataclass

import pandas as pd
import pytest

from tools.finance_utils import sim_payoff_bootstrapped

sample_series = pd.Series({
        pd.to_datetime("2013-12-31"): 0.25,
        pd.to_datetime("2014-12-31"): 0.42,
        pd.to_datetime("2015-12-31"): -0.25,
        pd.to_datetime("2016-12-31"): -0.33,
        pd.to_datetime("2017-12-31"): 0.02,
    })

@dataclass
class TestParameters:
    start_value = 1.42
    num_scenarios: int = 100

parameters = TestParameters()

@pytest.mark.parametrize("mean", [sample_series.mean(), 0.05])
@pytest.mark.parametrize("volatility", [sample_series.std(), 0.24])
def test_sim_payoff(mean: float, volatility: float) -> None:
    simulated_payoff = sim_payoff_bootstrapped(hist_returns=sample_series,
                                               num_scenarios=parameters.num_scenarios,
                                               start_value=parameters.start_value,
                                               mean=mean,
                                               volatility=volatility)

    assert simulated_payoff.mean() == pytest.approx(mean * parameters.start_value)
    assert simulated_payoff.std() == pytest.approx(volatility * parameters.start_value)
    assert len(simulated_payoff) == parameters.num_scenarios
