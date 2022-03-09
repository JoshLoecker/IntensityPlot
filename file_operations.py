import argparse
import pathlib
import plotly


def get_experiment_title(args: argparse.Namespace) -> str:
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


def get_output_file_name(args: argparse.Namespace) -> str:
    file_name = get_experiment_title(args)

    file_name = file_name.lower()
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")

    return file_name


def write_plot_to_file(
    plot: plotly.graph_objects.Figure,
    args: argparse.Namespace,
):
    """
    This function will simply handle writing the plotly graph to an output file

    :param plot: The plotly graph
    :param args: The arguments retrieved from the command line using arg_parse
    :return: None
    """

    file_name = get_output_file_name(args)
    file_name += ".html"

    # Place the html plot next to the input file
    output_path = pathlib.Path(args.input).parent
    output_file_path = output_path.joinpath(file_name)

    plot.write_html(output_file_path)
