"""
Project Goal
Take data from an input script and collect the following columns:
    1) Intensity dried_1
    2) Intensity dried_2
    3) Intensity dried_3
    4) Intensity liquid_1
    5) Intensity liquid_2
    6) Intensity liquid_3

From here, we should place these into a dataframe that ultimately looks like so
    (Index is given in a pandas dataframe)

    Index   gene_name   dried_1     dried_2     dried_3     liquid_1    liquid_2    liquid_3
    0       A           100         400         500         750         314         6876
    1       B           34          68          789         0           0           0
    .       .           .           .           .           .           .
    .       .           .           .           .           .           .
    .       .           .           .           .           .           .
    N       Z           N           N           N           N           N

From here, we can use plotly to create a simple scatter plot with gene names
"""
import pathlib
import csv
import pandas as pd
import sys
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go


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
    intensities["size"] = round(
        intensities[["dried_variation", "liquid_variation"]].mean(axis=1) * 10000000, 4
    )

    # Replace NA with -1
    # This is required because some averages are 0, and dividing by 0 = NaN
    intensities = intensities.fillna(-1)

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


def get_regression_results(plot: plotly.graph_objs.Figure) -> None:
    regression_data: pd.DataFrame = px.get_trendline_results(plot)
    fit_results = regression_data["px_fit_results"][0].pvalues
    raise NotImplementedError


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
    with open("clinicallyRelevant.txt", "r") as i_stream:
        relevant_proteins: list[str] = i_stream.readlines()

    return pd.DataFrame()


def make_plot(
    intensities: pd.DataFrame,
    output_path: pathlib.Path,
    output_file_name: str = "intensityPlot.html",
) -> None:
    plot_df: pd.DataFrame = intensities[
        [
            "gene_name",
            "dried_average",
            "liquid_average",
            "dried_variation",
            "liquid_variation",
            "size",
        ]
    ]

    plot = px.scatter(
        data_frame=plot_df,
        x="dried_average",
        y="liquid_average",
        hover_name="gene_name",
        error_x=plot_df["dried_variation"],
        error_y=plot_df["liquid_variation"],
        trendline="ols",
    )

    customdata = np.stack(
        (
            plot_df["gene_name"],
            plot_df["dried_variation"],
            plot_df["liquid_variation"],
        ),
        axis=-1,
    )

    # TODO: Determine if 'hovermode="x unified"' is good
    plot.update_traces()
    plot.update_layout(title=get_experiment_title(output_path), hovermode="x unified")
    plot.update_xaxes(title_text="Dried Average Intensity")
    plot.update_yaxes(title_text="Liquid Average Intensity")

    write_out: pathlib.Path = output_path.joinpath(output_file_name)
    plot.write_html(write_out)


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
            make_plot(intensities=statistics_df, output_path=output_path)
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
