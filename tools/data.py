import pandas as pd


class HistoricalData:
    def __init__(self, data_path: str, start_date: str | None = None):
        self._time_series = self._load(data_path, start_date)

    def _load(self, path: str, start_date: str | None) -> pd.Series:
        hist_data = pd.read_csv(path, index_col="Date")

        if hist_data.shape[1] > 1:
            msg = f"""Historical data expected to have one column
                        only (representing time series of returns).
                        Got {hist_data.shape[1]} instead"""

            raise ValueError(msg)

        time_series = hist_data.iloc[:, 0].dropna()

        # ensure that the index has pd.Timestamp type
        time_series.index = [pd.to_datetime(d) for d in time_series.index]

        time_series = time_series.loc[start_date:]

        return time_series

    @property
    def num_timesteps(self) -> int:
        return len(self._time_series)

    @property
    def first_date(self) -> pd.Timestamp:
        return self._time_series.index[0]

    @property
    def series(self) -> pd.Series:
        return self._time_series

    @property
    def mean(self) -> float:
        return self._time_series.mean()

    @property
    def volatility(self) -> float:
        return self._time_series.std()

    @property
    def skewness(self) -> float:
        return self._time_series.skew()
