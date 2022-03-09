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

        # Remove albumin from our calculations, it is a large outlier
        data_frame = data_frame[data_frame["gene_name"] != "ALB"]

        x_values = np.array(data_frame["liquid_average"]).reshape((-1, 1))
        y_values = np.array(data_frame["dried_average"])

        self.__linear_regression = LinearRegression()
        self.__linear_regression.fit(X=x_values, y=y_values)

        self.linear_fit: np.ndarray = self.__linear_regression.predict(x_values)

        self.__calculate_r_squared = float(
            self.__linear_regression.score(X=x_values, y=y_values)
        )

    @property
    def slope(self) -> float:
        return float(self.__linear_regression.coef_)

    @property
    def y_intercept(self) -> float:
        return float(self.__linear_regression.intercept_)

    @property
    def r_squared(self) -> float:
        return self.__calculate_r_squared


def calculate_statistics(intensities: pd.DataFrame) -> pd.DataFrame:
    """
    This function will calculate various statistics required for graph creation

    :param intensities: The pandas dataframe containing various intensity values for liquid/dried experiments
    :return: A pandas dataframe with additional statistics
    """
    # Calculate averages
    intensities["dried_average"] = round(
        intensities[["dried_1", "dried_2", "dried_3"]].mean(axis=1), 4
    )
    intensities["liquid_average"] = round(
        intensities[["liquid_1", "liquid_2", "liquid_3"]].mean(axis=1), 4
    )

    # Calculate standard deviations
    intensities["dried_std_dev"] = round(
        intensities[["dried_1", "dried_2", "dried_3"]].std(axis=1), 4
    )
    intensities["liquid_std_dev"] = round(
        intensities[["liquid_1", "liquid_2", "liquid_3"]].std(axis=1), 4
    )

    # Calculate coefficient of variation
    intensities["dried_variation"] = round(
        (intensities["dried_std_dev"] / intensities["dried_average"]) * 100, 4
    )
    intensities["liquid_variation"] = round(
        intensities["liquid_std_dev"] / intensities["liquid_average"] * 100, 4
    )

    # Calculate ratio of dried:liquid
    intensities["dried_liquid_ratio"] = round(
        intensities["dried_average"] / intensities["liquid_average"], 4
    )

    # Calculate size of bubble for bubble graph
    intensities["average_variation"] = round(
        intensities[["dried_variation", "liquid_variation"]].mean(axis=1), 4
    )

    # Some averages are 0 (or inf), and dividing by 0 = NaN
    # Fix this by resetting values to 0 and changing inf values to zero
    intensities.fillna(0, inplace=True)
    intensities[intensities["dried_liquid_ratio"] == np.inf] = 0
    intensities.reset_index(drop=True, inplace=True)

    return intensities
