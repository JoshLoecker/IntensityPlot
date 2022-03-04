import pandas as pd
import pathlib
import plotly


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
