import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


class CalculateLinearRegression:
    def __init__(self, data_frame: pd.DataFrame):
        """
        Calculate the trendline required for linear regression

        From: https://stackoverflow.com/questions/65135524/adding-trendline-on-plotly-scatterplot
        :param data_frame:
        :return:
        """

        x_values = np.array(data_frame["dried_average"]).reshape((-1, 1))
        y_values = np.array(data_frame["liquid_average"])

        self.__linear_regression = LinearRegression()
        self.__linear_regression.fit(
            X=x_values,
            y=y_values,
        )

        self.linear_fit: np.ndarray = self.__linear_regression.predict(x_values)

        self.slope = float(self.__linear_regression.coef_)
        self.y_intercept = float(self.__linear_regression.intercept_)
        self.r_squared = float(self.__linear_regression.score(X=x_values, y=y_values))
