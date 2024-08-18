import streamlit as st

from utils import compute_portfolio_stats

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

with column_2:
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

with column_1:
    years_after_retire = st.slider(label="Years after retirement",
                            min_value=0,
                            max_value=50,
                            value=20,
                            step=1,
                            help="How many years you plan to spend in retirement")

portfolio_stats = compute_portfolio_stats(start_value=start_value,
                                          years_before_ret=years_before_retire,
                                          years_after_ret=years_after_retire,
                                          yearly_installment=yearly_installment,
                                          yearly_withdrawls=yearly_withdrawl,
                                          num_scenarios=100_000,
                                          start_date="1945-12-31")

columns_to_plot = ["Mean", "Median"]
st.line_chart(portfolio_stats[columns_to_plot], x_label="Years from now", y_label="Portfolio value")

if st.checkbox("Show invested / withdrawn data (chart)"):
    columns_to_plot = ["Total invested", "Total withdrawn",
                       "Total mean return", "Total median return"]
    st.line_chart(portfolio_stats[columns_to_plot], x_label="Years from now", y_label="Amount")

if st.checkbox("Show all data (table)"):
    st.dataframe(portfolio_stats)

st.markdown("""
### Description and methodology

At the first stage (before retirement) it is assumed that you invest constant amount of money.
At the second stage (after retirement) it is assumed that you only withdraw from your investment account.

Simulation is based on the historical US **equity data** from [Shiller's website](http://www.econ.yale.edu/~shiller/data.htm).
Therefore, it is assumed that your investment portfolio consists 100 percent of US equity stocks (S&P 500).

All values are in **real** terms (adjusted for inflation).
This is possible because Shiller's data contains real (as well as nominal) returns.
This is convenient, because we can view our portolio value in today's money and don't need to adjust for inflation.

We use bootstaping to simulate 100000 scenarios.
We use data from the post World War II period (1945-12-31).
We assume that yearly returns are i.i.d. (but not (log-)normal).
Data from 1945 to 2023 has average yearly return of 5.3% and volatility 16.5% (skewness -0.3).

The main chart below display mean and median portfolio values.
Mean and median diverge significantly because our portfolio value becomes right skewed.
It is best to use median over mean for this kind of the long term financial planning.
It tells you minimum amount of money you should expect have in a given year in 50% of the cases
(or, equivalently, maximum amount of money in worst half of the scenarios).

Even better, you should check 25th (or 5th) percentiles which are available in the table below that page.
5th percentile is Value at Risk 5%.
You can interpret it as a portfolio value is bad long term market environment.
""")
