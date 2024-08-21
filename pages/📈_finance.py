import pandas as pd
import streamlit as st

from charting import get_hist_plot, get_invested_withdrawn_plot, get_stats_plot
from tools import HistoricalData, compute_portfolio_stats, load_config

config = load_config()

st.markdown("""
## Financial Planner

This tool is designed for financial planning.
It should be used for indicative purposes only and is not financial advice.
Actual results may significantly differ from simulated values.
This tool, methodology, and code behind it are based on my personal judgment and do not reflect
the views of any other institution.

The Financial Planner lets you estimate how much you should invest for a comfortable retirement.
Given your input data, it will simulate a portfolio value until the end of your retirement.
Check out the description and methodology sections below.
""")

column_1, column_2 = st.columns(2)

with column_1:
    start_value = st.slider(label="Start amount",
                            min_value=0,
                            max_value=100_000,
                            value=10_000,
                            step=5_000,
                            help="Initial amount of investment (now)")

with column_1:
    yearly_installment = st.slider(label="Yearly installment",
                                   min_value=0,
                                   max_value=100_000,
                                   value=10_000,
                                   step=5_000,
                                   help="Additional investment every year (before retirement)")

with column_1:
    yearly_withdrawl = st.slider(label="Yearly withdrawl",
                                 min_value=0,
                                 max_value=200_000,
                                 value=50_000,
                                 step=5_000,
                                 help="Yearly withdrawls from the account (after retirement)")

with column_2:
    years_before_retire = st.slider(label="Years before retirement",
                                    min_value=0,
                                    max_value=70,
                                    value=30,
                                    step=1,
                                    help="In how many years do you plan to retire")

with column_2:
    years_after_retire = st.slider(label="Years after retirement",
                                   min_value=0,
                                   max_value=50,
                                   value=20,
                                   step=1,
                                   help="How many years you plan to spend in retirement")

with column_2:
    start_date = st.date_input("Start date",
                               value=pd.to_datetime("1949-12-31"),
                               min_value=pd.to_datetime("1889-12-31"),
                               max_value=pd.to_datetime("2023-12-31"),
                               help="Start date for the historical data (used for bootstrapping)")

hist_data = HistoricalData(config.hist_returns_path, start_date.isoformat())

# TODO: remove leverage
with st.expander("Advanced settings"):
    adv_col_1, adv_col_2, adv_col_3 = st.columns(3)
    with adv_col_1:
        mean = st.number_input("Mean",
                               value=hist_data.mean,
                               format="%0.3f",
                               step=0.001,
                               help="Mean yearly return")
    with adv_col_2:
        volatility = st.number_input("Volatility",
                                     min_value=0.0,
                                     value=hist_data.volatility,
                                     format="%0.3f",
                                     step=0.01,
                                     help="Volatility of yearly returns")
    with adv_col_3:
        leverage = st.slider("Leverage",
                                   min_value=1.0,
                                   max_value=3.0,
                                   value=1.0,
                                   step=1.0,
                                   help="Portfolio leverage. Please note that leverage is associated with very high risks. Leverage costs are not taken into account.")

portfolio_stats = compute_portfolio_stats(hist_values=hist_data.series,
                                          start_value=start_value,
                                          years_before_ret=years_before_retire,
                                          years_after_ret=years_after_retire,
                                          yearly_installment=yearly_installment,
                                          yearly_withdrawls=yearly_withdrawl,
                                          num_scenarios=100_000,
                                          mean=mean,
                                          volatility=volatility,
                                          leverage=leverage)

show_mean = st.checkbox("Show mean")

st.plotly_chart(get_stats_plot(portfolio_stats, show_mean))
st.plotly_chart(get_invested_withdrawn_plot(portfolio_stats))

stat_columns_dict = {
    "Median": "Median",
    "Percentile 25": "VaR 75%",
    "Percentile 5": "VaR 95%",
}
df_last_timestep = portfolio_stats[stat_columns_dict.keys()].rename(columns=stat_columns_dict).iloc[-1]
df_last_timestep.name = "Last year"
st.dataframe(df_last_timestep)

if st.checkbox("Show hist data (chart)"):
    st.plotly_chart(get_hist_plot(hist_data.series))

if st.checkbox("Show hist data stats"):
    hist_stats = pd.Series({
        "Mean": hist_data.mean,
        "Volatility": hist_data.volatility,
        "Skewness": hist_data.skewness,
        "Min": hist_data.series.min(),
        "Max": hist_data.series.max(),
        "Num points": hist_data.num_timesteps,
    })
    hist_stats.name = "Hist stats"

    st.dataframe(hist_stats)


if st.checkbox("Show all data (table)"):
    st.dataframe(portfolio_stats)

st.markdown(f"""
### Description and methodology

At the first stage (before retirement), it's assumed that you invest a constant amount of money.
At the second stage (after retirement), it's assumed that you only withdraw from your
investment account.

The simulation is based on historical US **equity data** from
[Shiller's website](http://www.econ.yale.edu/~shiller/data.htm).
It assumes that your investment portfolio consists of 100% US equity stocks (S&P 500).

All values are in **real** terms (adjusted for inflation).
This is possible because Shiller's data contains both real and nominal returns.
It's convenient, as we can view our portfolio value in today's money without
needing to adjust for inflation.

Please note that taxes and fund fees are not taken into account.

We use bootstrapping to simulate 100,000 scenarios.
By default, we use data from the post-World War II period (starting from 1949-12-31).
We assume that yearly returns are i.i.d. (but not (log-)normal).
Data from {hist_data.first_date.year} to 2023 ({hist_data.num_timesteps} datapoints)
has an average yearly return of {hist_data.mean * 100:.1f}% and
volatility of {hist_data.volatility * 100:.1f}% (skewness {hist_data.skewness:.1f}).

The main chart below displays mean and median portfolio values.
Mean and median diverge significantly because our portfolio value becomes right-skewed.
It's best to use the median over the mean for this kind of long-term financial planning.
It tells you the minimum amount of money you should expect to have in a given year
in 50% of the cases (or, equivalently, the maximum amount of money in the worst
half of the scenarios).

Even better, you should check the 25th (or 5th) percentiles,
which are available in the table below. The 5th percentile represents the
Value at Risk (VaR) at 5%. You can interpret it as the portfolio value in a bad long-term
market environment.
""")

st.page_link("home.py", icon="🏠")
