import pandas as pd


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
