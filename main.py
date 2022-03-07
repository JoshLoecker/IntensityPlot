import filter_values
import statistics
import file_operations
import plot_generation

import csv
import thefuzz as fuzzy_search
import pandas as pd
import pathlib
import plotly
import plotly.express as px
import plotly.graph_objects as go
import sys


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
        "protein_id": [],
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
            intensities["protein_id"].append(line[1])
            intensities["gene_name"].append(line[6])
            intensities["protein_name"].append(line[5])
            intensities["dried_1"].append(int(float(line[51])))
            intensities["dried_2"].append(int(float(line[52])))
            intensities["dried_3"].append(int(float(line[53])))
            intensities["liquid_1"].append(int(float(line[54])))
            intensities["liquid_2"].append(int(float(line[55])))
            intensities["liquid_3"].append(int(float(line[56])))

    return pd.DataFrame(intensities)


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        output_path = input_file.parent

        if input_file.match("proteinGroups.txt"):
            liquid_vs_dried_intensity = create_intensity_dataframe(
                input_file=input_file
            )
            liquid_vs_dried_intensity = statistics.calculate_statistics(
                intensities=liquid_vs_dried_intensity
            )
            liquid_vs_dried_intensity = filter_values.filter_variation(
                liquid_vs_dried_intensity
            )
            liquid_vs_dried_intensity = filter_values.filter_clinically_relevant(
                liquid_vs_dried_intensity
            )

            liquid_vs_dried_intensity_plot = (
                plot_generation.liquid_intensity_vs_dried_intensity(
                    intensities=liquid_vs_dried_intensity, input_data=input_file
                )
            )

            file_operations.write_intensities(
                data_frame=liquid_vs_dried_intensity, output_path=output_path
            )
            file_operations.write_plot_to_file(
                liquid_vs_dried_intensity_plot, output_path
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
