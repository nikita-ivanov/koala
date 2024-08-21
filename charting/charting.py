import pandas as pd
import plotly.graph_objects as go


def get_stats_plot(portfolio_stats: pd.DataFrame, show_mean: bool = False) -> go.Figure:
    fig = go.Figure()

    x_axis_shade_area = portfolio_stats.index.to_list()
    x_axis_shade_area += portfolio_stats.index.to_list()[::-1]

    y_axis_shade_area = portfolio_stats["Percentile 75"].to_list()
    y_axis_shade_area += portfolio_stats["Percentile 25"].to_list()[::-1]

    fig.add_trace(go.Scatter(x=x_axis_shade_area,
                            y=y_axis_shade_area,
                            fill="toself",
                            fillcolor="rgba(0,150,200,0.1)",
                            line_color="rgba(255,255,255,0)",
                            showlegend=False))

    fig.add_trace(go.Scatter(x=portfolio_stats.index,
                            y=portfolio_stats["Median"],
                            mode="lines+markers",
                            name="Median"))

    if show_mean:
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

    return fig

def get_hist_plot(hist_series: pd.Series) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=hist_series.index,
                             y=hist_series,
                             mode="lines+markers",
                             line={"color": "lightblue"}))

    fig.update_layout(yaxis_title="Real return",
                      title="Historical real returns")

    return fig

def get_invested_withdrawn_plot(portfolio_stats: pd.DataFrame) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(x=portfolio_stats.index,
                             y=portfolio_stats["Total invested"],
                             name="Total invested"))

    fig.add_trace(go.Scatter(x=portfolio_stats.index,
                             y=portfolio_stats["Total withdrawn"],
                             name="Total withdrawn"))

    fig.update_layout(xaxis_title="Years from now",
                    yaxis_title="Amount",
                    title="Invested and withdrawn amounts",
                    legend={"yanchor": "top",
                            "y": 0.99,
                            "xanchor": "left",
                            "x": 0.01})

    return fig
