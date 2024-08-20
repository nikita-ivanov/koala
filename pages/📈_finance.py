import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from tools import HistoricalData, compute_portfolio_stats, load_config

config = load_config()

st.markdown("""
## Financial Planner

This tool is designed for the financial planning.
It should be used for indicative purposes only and is not a financial advise.
Actual results might significantly differ from simulated values.
This tool, methodology, and code behind it are based on my personal judgment and do not reflect
views of any other institution.

Financial planner lets you estimate how much you should invest for a comfortable retirement.
Given your input data, it will simulate a profolio value until end of your retirement.
Check out description  and methodology section below.
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

fig = go.Figure()

fig.add_trace(go.Scatter(x=portfolio_stats.index.to_list() + portfolio_stats.index.to_list()[::-1],
                         y=portfolio_stats["Percentile 75"].to_list() + portfolio_stats["Percentile 25"].to_list()[::-1],
                         fill="toself",
                         fillcolor="rgba(0,176,246,0.2)",
                         line_color="rgba(255,255,255,0)",
                         showlegend=False))

fig.add_trace(go.Scatter(x=portfolio_stats.index,
                         y=portfolio_stats["Median"],
                         mode="lines+markers",
                         name="Median",
                         line=dict(color="blue")))

if st.checkbox("Show mean"):
    fig.add_trace(go.Scatter(x=portfolio_stats.index,
                            y=portfolio_stats["Mean"],
                            mode="lines+markers",
                            name="Mean",
                            line={"color": "red"}))

fig.update_layout(xaxis_title="Years from now",
                  yaxis_title="Portfolio value",
                  title="Median porfolio value with 25th and 75th percentiles",
                  legend={"yanchor": "top",
                          "y": 0.99,
                          "xanchor": "left",
                          "x": 0.01})

st.plotly_chart(fig)

stat_columns_dict = {
    "Median": "Median",
    "Percentile 25": "VaR 75%",
    "Percentile 5": "VaR 95%",
}
df_last_timestep = portfolio_stats[stat_columns_dict.keys()].rename(columns=stat_columns_dict).iloc[-1]
st.dataframe(df_last_timestep)

# TODO: refactor all other charts to plotly
# TODO: refactor charting into separate module
if st.checkbox("Show hist data stats"):
    st.dataframe(pd.Series({
        "Mean": hist_data.mean,
        "Volatility": hist_data.volatility,
        "Skewness": hist_data.skewness,
        "Min": hist_data.series.min(),
        "Max": hist_data.series.max(),
        "Num points": hist_data.num_timesteps,
    }).transpose())

if st.checkbox("Show hist data (chart)"):
    st.line_chart(hist_data.series, x_label="Date", y_label="Real return")

if st.checkbox("Show invested / withdrawn data (chart)"):
    columns_to_plot = ["Total invested", "Total withdrawn"]
    st.line_chart(portfolio_stats[columns_to_plot], x_label="Years from now", y_label="Amount")

if st.checkbox("Show all data (table)"):
    st.dataframe(portfolio_stats)

st.markdown(f"""
### Description and methodology

At the first stage (before retirement) it is assumed that you invest constant amount of money.
At the second stage (after retirement) it is assumed that you only withdraw from your investment account.

Simulation is based on the historical US **equity data** from [Shiller's website](http://www.econ.yale.edu/~shiller/data.htm).
Therefore, it is assumed that your investment portfolio consists 100 percent of US equity stocks (S&P 500).

All values are in **real** terms (adjusted for inflation).
This is possible because Shiller's data contains real (as well as nominal) returns.
This is convenient, because we can view our portolio value in today's money and don't need to adjust for inflation.

Please note that taxes are not taken into account.

Currently no fund fees are taken into account.

We use bootstaping to simulate 100000 scenarios.
We use data from the post World War II period (from 1949-12-31) by default.
We assume that yearly returns are i.i.d. (but not (log-)normal).
Data from {hist_data.first_date.year} to 2023 ({hist_data.num_timesteps} datapoints)
has average yearly return of {hist_data.mean * 100:.1f}%
and volatility {hist_data.volatility * 100:.1f}% (skewness {hist_data.skewness:.1f}).

The main chart below display mean and median portfolio values.
Mean and median diverge significantly because our portfolio value becomes right skewed.
It is best to use median over mean for this kind of the long term financial planning.
It tells you minimum amount of money you should expect have in a given year in 50% of the cases
(or, equivalently, maximum amount of money in worst half of the scenarios).

Even better, you should check 25th (or 5th) percentiles which are available in the table below that page.
5th percentile is Value at Risk 5%.
You can interpret it as a portfolio value is bad long term market environment.
""")
