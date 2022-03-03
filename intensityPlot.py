import clinically_relevant
import csv
import thefuzz as fuzzy_search
import numpy as np
import pandas as pd
import pathlib
import plotly
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import sys


class RegressionRetrieval:
    """
    This is a simple class to retrieve regression information from a plotly express graph
    This was created to ensure it was easy to retrieve the requested value correctly

    If a function returned y_intercept, slope, and r_squared, it may be confusing to determine
        in which order these variables are being returned in

    A class fixes this by allowing users to use the "dot operator" to retrieve the correct value

    When passing in the 'plot' parameter, the 'trendline' option for plotly express graphs (or similar) should be used
        https://plotly.com/python/linear-fits/
    """

    def __init__(self, data_frame: pd.DataFrame, plot: plotly.graph_objects.Figure):

        # These values are hidden from public access using a double underscore
        self.__regression_data: pd.DataFrame = px.get_trendline_results(plot)
        self.__regression_model = self.__regression_data["px_fit_results"][0]
        self.__summary = self.__regression_model.summary()
        self.__data_frame = data_frame

        self.y_intercept: float = self.__regression_model.params[0]
        self.slope: float = self.__regression_model.params[1]
        self.r_squared: float = self.__regression_model.rsquared


def create_intensity_dataframe(input_file: pathlib.Path) -> pd.DataFrame:
    """
    This function will gather a series of data from the input file
    These data will be:
        1) The identified gene name
        2) The identified protein name
        3) All dried intensity values
        4) All liquid intensity values

    It will return these items as a pandas dataframe

    :param input_file: The MaxQuant proteinGroups.txt results file
    :return: A pandas dataframe
    """
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

        # Remove the header, as it is not required
        next(reader)

        for line in reader:
            # Convert values to an integer, as the specifics of a float are not required
            intensities["gene_name"].append(line[6])
            intensities["protein_name"].append(line[5])
            intensities["dried_1"].append(int(float(line[51])))
            intensities["dried_2"].append(int(float(line[52])))
            intensities["dried_3"].append(int(float(line[53])))
            intensities["liquid_1"].append(int(float(line[54])))
            intensities["liquid_2"].append(int(float(line[55])))
            intensities["liquid_3"].append(int(float(line[56])))

    return pd.DataFrame(intensities)


def write_intensities(
    data_frame: pd.DataFrame,
    output_path: pathlib.Path,
    file_name: str = "intensityPlot.csv",
) -> None:
    """
    This function will write the input dataframe to the specified output path and file name

    :param data_frame: The data frame to write
    :param output_path: The path/folder to write the dataframe to
    :param file_name: The name for the file
    :return: None
    """
    output_file: pathlib.Path = pathlib.Path(output_path, file_name)
    data_frame.to_csv(output_file, index=False)


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

    intensities["plot_marker_size"] = round(
        (intensities["dried_variation"] + intensities["liquid_variation"]) / 2, 4
    )

    # Some averages are 0, and dividing by 0 = NaN
    # Fix this by resetting values to 0
    intensities = intensities.fillna(0)

    return intensities


def get_experiment_title(file_path: pathlib.Path) -> str:
    """
    This function is used to determine what type of experiment we are dealing with

    It is very specific to the testing data currently available
    This function should most likely be included to accept a parameter (or read from a configuration file) to determine the experiment name

    :param file_path: The file path where the proteinGroups.txt file is located
    :return: A string containing the name of the experiment
    """
    str_file_path: str = str(file_path).lower()
    title: str = ""

    # Found "direct" in the file path
    if str_file_path.find("direct") != -1:
        title += "Direct-"
    # Found "c18" in the file path
    elif str_file_path.find("c18") != -1:
        title += "C18-"

    # Found "urea" in the file path
    if str_file_path.find("urea") != -1:
        title += "Urea "
    # Found "sdc" in the file path
    elif str_file_path.find("sdc") != -1:
        title += "SDC "

    # Always append 'Experiment'. This is in case we could not find one of the specified cases above
    title += "Experiment"

    return title


def filter_variation(data_frame: pd.DataFrame, max_variation: int = 20) -> pd.DataFrame:
    """
    This function will filter variation values

    Any variantion values LESS THAN max_variation will be accepted
    We must also filter GREATER THAN 0 because NaN values in the dataframe have been set to 0

    We are currently accepting liquid OR dried variation less than max_variation

    :param data_frame: The dataframe to filter from
    :param max_variation: The maximum variation value to accept
    :return: A pandas dataframe containing the filtered values
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
    :return: A new dataframe containing the intersect of MaxQuant proteins and clinically relevant proteins
    """
    intersect_df: pd.DataFrame = pd.DataFrame()

    return intersect_df


def make_plot(
    intensities: pd.DataFrame,
    input_data: pathlib.Path,
) -> plotly.graph_objects.Figure:
    """
    This function is responsible for creating the final Plotly graph


    :param intensities: The dataframe containing intensity values from MaxQuant
    :param input_data: The path for the input data
    :return: A plotly.graph_objects.Figure
    """

    # Create a new dataframe to filter the values we need
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

    # Create the plot
    plot = px.scatter(
        data_frame=plot_df,
        x="dried_average",
        y="liquid_average",
        error_x="dried_variation",
        error_y="liquid_variation",
        trendline="ols",
        size="plot_marker_size",
        custom_data=[
            plot_df["gene_name"],
            plot_df["plot_marker_size"],
        ],
    )

    # Retrieve regression data
    regression_calculation = RegressionRetrieval(plot_df, plot)

    # Add axis labels
    plot.update_layout(title=get_experiment_title(input_data))
    plot.update_xaxes(title_text="Dried Average Intensity")
    plot.update_yaxes(title_text="Liquid Average Intensity")

    # Add hover template
    plot.update_traces(
        hovertemplate="<br>".join(
            [
                "Gene Name: %{customdata[0]}",
                "Dried Average: %{x}%",
                "Liquid Average: %{y}%",
                "Average Variation: ± %{customdata[1]}%",
            ]
        )
    )

    # Add linear regression equation as an annotation
    regression_equation = "<br>".join(
        [
            f"(Liquid Average) = {regression_calculation.slope:.3f} * (Dried Average) + {regression_calculation.y_intercept:.3e}",
            f"R² = {regression_calculation.r_squared:.3f}",
            f"Unique proteins identified = {len(plot_df['gene_name'].values)}",
        ]
    )
    plot.add_annotation(
        text=regression_equation,
        showarrow=False,
        x=1,
        y=0,
        xref="paper",
        yref="paper",
        align="right",
    )

    return plot


def write_plot_to_file(
    plot: plotly.graph_objects.Figure,
    file_path: pathlib.Path,
    file_name: str = "intensityPlot",
):
    """
    This function will simply handle writing the plotly graph to an output file

    :param plot: The plotly graph
    :param file_path: The path/folder to save the graph
    :param file_name: The name of the output file, EXCLUDING the file extension
    :return: None
    """
    # If an extension is found in file_name
    if pathlib.Path(file_name).suffix != "":
        print(
            f"Sorry, there appears to be an extension in your 'file_name' parameter for the {write_plot_to_file.__name__} function"
        )
        exit(1)

    file_name = get_experiment_title(file_path)
    file_name = file_name.lower()
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")
    file_name += ".html"

    output_path: pathlib.Path = file_path.joinpath(file_name)
    plot.write_html(output_path)


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        output_path = input_file.parent

        if input_file.match("proteinGroups.txt"):
            data_frame = create_intensity_dataframe(input_file=input_file)
            data_frame = calculate_statistics(intensities=data_frame)
            data_frame = filter_variation(data_frame)
            # data_frame = filter_clinically_relevant(data_frame)

            plot = make_plot(intensities=data_frame, input_data=input_file)
            write_intensities(data_frame=data_frame, output_path=output_path)
            write_plot_to_file(
                plot,
                output_path,
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
