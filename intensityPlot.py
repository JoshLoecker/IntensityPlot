import clinically_relevant
import csv
import thefuzz as fuzzy_search
import numpy as np
import pandas as pd
import pathlib
import plotly
import plotly.express as px
import plotly.graph_objects as go
import sys


class RegressionData:
    """
    This is a simple class to retrieve regression information from a plotly express graph
    This was created to ensure it was easy to retrieve the requested value correctly

    If a function returned y_intercept, slope, and r_squared, it may be confusing to determine
        in which order these variables are being returned in

    A class fixes this by allowing users to use the "dot operator" to retrieve the correct value

    When passing in the 'plot' parameter, the 'trendline' option for plotly express graphs (or similar) should be used
        https://plotly.com/python/linear-fits/
    """

    def __init__(self, plot: plotly.graph_objs.Figure):
        # These values are hidden from public access using a double underscore
        self.__regression_data: pd.DataFrame = px.get_trendline_results(plot)
        self.__regression_model = self.__regression_data["px_fit_results"][0]
        self.__summary = self.__regression_model.summary()

        self.y_intercept: float = round(self.__regression_model.params[0], 4)
        self.slope: float = round(self.__regression_model.params[1], 4)
        self.r_squared: float = round(self.__regression_model.rsquared, 4)


def get_intensity(input_file: pathlib.Path) -> pd.DataFrame:
    intensities: dict = {
        "gene_name": [],
        "protein_name": [],
        "dried_1": [],
        "dried_2": [],
        "dried_3": [],
        "liquid_1": [],
        "liquid_2": [],
        "liquid_3": [],
    }

    with open(input_file, "r") as i_stream:
        reader = csv.reader(i_stream, delimiter="\t")
        next(reader)

        for line in reader:
            intensities["gene_name"].append(line[6])
            intensities["protein_name"].append(line[5])
            intensities["dried_1"].append(int(float(line[51])))
            intensities["dried_2"].append(int(float(line[52])))
            intensities["dried_3"].append(int(float(line[53])))
            intensities["liquid_1"].append(int(float(line[54])))
            intensities["liquid_2"].append(int(float(line[55])))
            intensities["liquid_3"].append(int(float(line[56])))

    return pd.DataFrame.from_dict(intensities)


def write_intensities(intensities: pd.DataFrame, output_path: pathlib.Path) -> None:
    output_file: pathlib.Path = pathlib.Path(output_path, "intensityPlot.csv")
    intensities.to_csv(output_file, index=False)


def calculate_statistics(intensities: pd.DataFrame) -> pd.DataFrame:
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
    intensities["plot_marker_size"] = round(
        intensities[["dried_variation", "liquid_variation"]].mean(axis=1) * 10000000, 4
    )

    # Some averages are 0, and dividing by 0 = NaN
    # Fix this by resetting values to 0
    intensities = intensities.fillna(0)

    return intensities


def get_experiment_title(file_path: pathlib.Path) -> str:
    str_file_path: str = str(file_path).lower()
    title: str = ""

    if str_file_path.find("direct") != -1:
        title += "Direct-"

        if str_file_path.find("urea") != -1:
            title += "Urea "
        elif str_file_path.find("sdc") != -1:
            title += "SDC "

    elif str_file_path.find("c18") != -1:
        title += "C18-"

        if str_file_path.find("urea") != -1:
            title += "Urea "
        elif str_file_path.find("sdc") != -1:
            title += "SDC "

    # Always append 'Experiment'. This is in case we could not find one of the specified cases above
    title += "Experiment"

    return title


def filter_variation(data_frame: pd.DataFrame, max_variation: int = 20) -> pd.DataFrame:
    """
    Any variantion values LESS THAN max_variation will be accepted
    We must also filter GREATER THAN 0 because NaN values in the dataframe have been set to -1

    :param data_frame: The dataframe to filter from
    :param max_variation: The maximum variation value to accept
    :return: Nothing for now
    """

    return data_frame[
        (
            (0 < data_frame["dried_variation"])
            & (data_frame["dried_variation"] < max_variation)
        )
        | (
            (0 < data_frame["liquid_variation"])
            & (data_frame["liquid_variation"] < max_variation)
        )
    ]


def filter_clinically_relevant(data_frame: pd.DataFrame) -> pd.DataFrame:
    """
    This function will take an incoming dataframe and filter its protein_name column against clinically relevant proteins from the 'clinicallyRelevant.txt' file

    Use fuzzywuzzy as a search algorithm? https://pypi.org/project/fuzzywuzzy/

    :param data_frame: The incoming dataframe
    :return:
    """
    intersect_df: pd.DataFrame = pd.DataFrame()

    return intersect_df


def make_plot(
    intensities: pd.DataFrame,
    output_path: pathlib.Path,
    output_file_name: str = "intensityPlot.html",
) -> plotly.graph_objects.Figure:
    plot_df: pd.DataFrame = intensities[
        [
            "gene_name",
            "dried_average",
            "liquid_average",
            "dried_variation",
            "liquid_variation",
            "plot_marker_size",
        ]
    ]

    plot = px.scatter(
        data_frame=plot_df,
        x="dried_average",
        y="liquid_average",
        hover_name="gene_name",
        error_x="dried_variation",
        error_y="liquid_variation",
        trendline="ols",
        size="plot_marker_size",
    )
    regression_calculation = RegressionData(plot)

    # TODO: Determine if 'hovermode="x"' is good
    plot.update_layout(title=get_experiment_title(output_path), hovermode="x")
    plot.update_xaxes(title_text="Dried Average Intensity")
    plot.update_yaxes(title_text="Liquid Average Intensity")

    # Add linear regression line
    regression_equation: str = f"(Liquid Average) = {regression_calculation.slope} * (Dried Average) + {regression_calculation.y_intercept}"
    regression_equation += f"<br>R² = {regression_calculation.r_squared}"
    plot.add_annotation(
        text=regression_equation,
        showarrow=False,
        x=1,
        y=0,
        xref="paper",
        yref="paper",
        align="right",
    )

    write_out: pathlib.Path = output_path.joinpath(output_file_name)
    plot.write_html(write_out)

    return plot


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        output_path = input_file.parent

        if input_file.match("proteinGroups.txt"):
            intensities: pd.DataFrame = get_intensity(input_file=input_file)
            statistics_df: pd.DataFrame = calculate_statistics(intensities=intensities)
            filtered_variation: pd.Dataframe = filter_variation(statistics_df)
            filtered_clinically_relevant: pd.DataFrame = filter_clinically_relevant(
                filtered_variation
            )
            write_intensities(intensities=statistics_df, output_path=output_path)
            plot: plotly.graph_objs.Figure = make_plot(
                intensities=statistics_df, output_path=output_path
            )

        else:
            print(
                "You have not passed in the 'proteinGroups' text file. Please try again."
            )
            print("Make sure the file is named 'proteinGroups.txt'")

    except IndexError:
        print("You must pass in a file path as the first argument. Please try again")
        exit(1)


if __name__ == "__main__":
    main()
