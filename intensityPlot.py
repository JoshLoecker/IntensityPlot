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
import plotly.express as px


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
            intensities["dried_1"].append(float(line[51]))
            intensities["dried_2"].append(float(line[52]))
            intensities["dried_3"].append(float(line[53]))
            intensities["liquid_1"].append(float(line[54]))
            intensities["liquid_2"].append(float(line[55]))
            intensities["liquid_3"].append(float(line[56]))

    return pd.DataFrame.from_dict(intensities)


def write_intensities(intensities: pd.DataFrame, output_path: pathlib.Path):
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
    intensities["dried_variation"] = (
        intensities["dried_std_dev"] / intensities["dried_average"]
    )
    intensities["liquid_variation"] = (
        intensities["liquid_std_dev"] / intensities["liquid_average"]
    )

    return intensities


def make_plot(intensities: pd.DataFrame, output_path: pathlib.Path):
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

    plot = px.scatter(
        plot_df,
        x="dried_average",
        y="liquid_average",
        hover_name="gene_name",
        error_x="dried_variation",
        error_y="liquid_variation",
    )

    plot.write_html(output_file)


def main():
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
