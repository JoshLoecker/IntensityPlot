import arg_parse

import pandas as pd
import pathlib
import plotly


def get_experiment_title(args: command_line_args.ArgParse) -> str:
    """
    This function is used to determine what type of experiment we are dealing with

    It is very specific to the testing data currently available
    This function should most likely be included to accept a parameter (or read from a configuration file) to determine the experiment name

    :param args: A commandline_args.ArgParse type that contains various information gained from the command line
    :return: A string containing the name of the experiment
    """
    method = str(args.method).lower()
    experiment = str(args.experiment).lower()

    title = ""

    # Found "direct" in the file path
    if method == "direct":
        title += "Direct-"
    # Found "c18" in the file path
    elif method == "c18":
        title += "C18-"

    # Found "urea" in the file path
    if experiment == "urea":
        title += "Urea "
    # Found "sdc" in the file path
    elif experiment == "sdc":
        title += "SDC "

    # Always append 'Experiment'. This is in case we could not find one of the specified cases above
    title += "Experiment"

    return title


def get_output_file_name(args: command_line_args.ArgParse):
    experiment_title = get_experiment_title(args)
    print(experiment_title)


def write_intensities(
    data_frame: pd.DataFrame,
    output_path: pathlib.Path,
    file_name: str = "intensityPlot.tsv",
) -> None:
    """
    This function will write the input dataframe to the specified output path and file name

    :param data_frame: The data frame to write
    :param output_path: The path/folder to write the dataframe to
    :param file_name: The name for the file
    :return: None
    """
    output_file: pathlib.Path = pathlib.Path(output_path, file_name)
    data_frame.to_csv(output_file, index=False, sep="\t")


def write_plot_to_file(
    plot: plotly.graph_objects.Figure,
    args: command_line_args.ArgParse,
):
    """
    This function will simply handle writing the plotly graph to an output file

    :param plot: The plotly graph
    :param args: The arguments retrieved from the command line using command_line_args
    :return: None
    """

    file_name = get_experiment_title(args)
    file_name = file_name.lower()
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")
    file_name += ".html"

    output_path = pathlib.Path(args.output)
    output_file = output_path.joinpath(file_name)

    plot.write_html(output_file)
