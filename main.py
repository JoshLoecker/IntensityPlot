import csv
import pathlib

import pandas as pd

import arg_parse
import excel_writer
import file_operations
import filter_values
import plot_generation
import statistics


def create_intensity_dataframe(input_file: pathlib.Path | str) -> pd.DataFrame:
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


def main():
    args = arg_parse.ArgParse()
    args = args.args

    intensities_df = create_intensity_dataframe(input_file=args.input)
    intensities_df = statistics.calculate_statistics(intensities=intensities_df)
    intensities_df = filter_values.filter_variation(intensities_df)
    intensities_df = filter_values.add_clinical_relevance(intensities_df)

    # Sort values based on protein name for easier viewing
    intensities_df.sort_values("protein_name", ignore_index=True, inplace=True)
    intensities_df.reset_index(drop=True, inplace=True)

    clinically_relevant_plot = plot_generation.liquid_intensity_vs_dried_intensity(
        intensities=intensities_df, args=args
    )
    file_operations.write_plot_to_file(plot=clinically_relevant_plot, args=args)

    # Write all proteins to excel file (i.e., write statistics_df)
    excel_writer.PlasmaTable(data_frame=intensities_df, args=args)


if __name__ == "__main__":
    main()
