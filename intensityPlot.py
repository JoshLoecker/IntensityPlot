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
import plotly.graph_objects as go


def get_intensity(input_file: pathlib.Path) -> pd.DataFrame:
    intensities: dict = {
        "gene_name": [],
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
    intensities["dried_average"] = intensities[["dried_1", "dried_2", "dried_3"]].mean(
        axis=1
    )
    intensities["liquid_average"] = intensities[
        ["liquid_1", "liquid_2", "liquid_3"]
    ].mean(axis=1)

    # Calculate standard deviations
    intensities["dried_std_dev"] = intensities[["dried_1", "dried_2", "dried_3"]].std(
        axis=1
    )
    intensities["liquid_std_dev"] = intensities[
        ["liquid_1", "liquid_2", "liquid_3"]
    ].std(axis=1)

    # Calculate coefficient of variation
    intensities["dried_variation"] = round(
        intensities["dried_std_dev"] / intensities["dried_average"] * 100, 2
    )
    intensities["liquid_variation"] = round(
        intensities["liquid_std_dev"] / intensities["liquid_average"] * 100, 2
    )

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


def make_plot(intensities: pd.DataFrame, output_path: pathlib.Path) -> None:
    output_file: pathlib.Path = pathlib.Path(output_path, "intensityPlot.html")
    plot_df: pd.DataFrame = intensities[
        [
            "gene_name",
            "dried_average",
            "liquid_average",
            "dried_variation",
            "liquid_variation",
        ]
    ]
    # https://chart-studio.plotly.com/~empet/15366/customdata-for-a-few-plotly-chart-types/#/
    # Documentation: https://plotly.com/python/line-and-scatter/#simple-scatter-plot

    # Create an array of gene_name, dried_variation, liquid_variation in order to use it in our hover template
    customdata = np.stack(
        (
            plot_df["gene_name"],
            plot_df["dried_variation"],
            plot_df["liquid_variation"],
        ),
        axis=-1,
    )

    plot_new = go.Figure(
        go.Scatter(
            x=plot_df["dried_average"],  # Define 'x' values
            y=plot_df["liquid_average"],  # Define 'y' values
            customdata=customdata,  # Define custom data to use
            mode="markers",  # Use a true scatter plot, not line graph
            hovertemplate="Gene Name: %{customdata[0]}"
            + "<br>Dried Average: %{x} ± %{customdata[1]:.2f}%"
            + "<br>Liquid Average: %{y} ± %{customdata[2]:.2f}%"
            + "<extra></extra>",  # Define the template to use for hover data. '<br>' is a line break
        )
    ).update_layout(title=get_experiment_title(output_path))

    plot_new.write_html(output_file)


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        output_path = input_file.parent

        if input_file.match("proteinGroups.txt"):
            intensities: pd.DataFrame = get_intensity(input_file=input_file)
            statistics_df: pd.DataFrame = calculate_statistics(intensities=intensities)
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
