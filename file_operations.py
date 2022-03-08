import arg_parse

import pandas as pd
import pathlib
import plotly

import excel_writer


def get_experiment_title(args: arg_parse.ArgParse) -> str:
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


def get_output_file_name(args: arg_parse.ArgParse) -> str:
    file_name = get_experiment_title(args)

    file_name = file_name.lower()
    file_name = file_name.replace(" ", "_")
    file_name = file_name.replace("-", "_")

    return file_name


def write_excel_file(data_frame: pd.DataFrame, args: arg_parse.ArgParse):
    output_file = f"{get_output_file_name(args)}.xlsx"
    output_directory = pathlib.Path(str(args.output))
    output_path = output_directory.joinpath(output_file)

    print(output_path)

    write_excel = excel_writer.PlasmaTable(
        sheet_title="All Proteins",
        is_clinically_relevant=False,
        workbook_save_path=output_path,
    )


def write_plot_to_file(
    plot: plotly.graph_objects.Figure,
    args: arg_parse.ArgParse,
):
    """
    This function will simply handle writing the plotly graph to an output file

    :param plot: The plotly graph
    :param args: The arguments retrieved from the command line using arg_parse
    :return: None
    """

    file_name = get_output_file_name(args)
    file_name += ".html"

    output_path = pathlib.Path(args.output)
    output_file = output_path.joinpath(file_name)

    plot.write_html(output_file)
