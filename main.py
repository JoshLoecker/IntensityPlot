import filter_values
import statistics
import file_operations

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


def make_plot(
    intensities: pd.DataFrame,
    input_data: pathlib.Path,
) -> plotly.graph_objects.Figure:
    """
    This function is responsible for creating the final Plotly graph


    :param intensities: The dataframe containing intensity values from MaxQuant
    :param input_data: The path for the input data
    :return: A plotly.graph_objects.Figure
    """

    # Create a new dataframe to filter the values we need
    plot_df: pd.DataFrame = intensities[
        [
            "gene_name",
            "protein_id",
            "dried_average",
            "liquid_average",
            "dried_variation",
            "liquid_variation",
            "average_variation",
        ]
    ]

    # Calculate information required to create a trendline trace
    trendline = statistics.CalculateLinearRegression(plot_df)

    # Create the plot
    plot = go.Figure()
    # Bubble size is set to dried variation
    plot.add_trace(
        go.Scatter(
            x=plot_df["liquid_average"],
            y=plot_df["dried_average"],
            mode="markers",
            marker=dict(
                size=plot_df["dried_variation"].values.tolist(),
                sizemode="area",
                # Calculate max size of bubble. From: https://plotly.com/python/bubble-charts/#scaling-the-size-of-bubble-charts
                sizeref=2.0 * plot_df["dried_variation"].max() / (40.0**2),
                sizemin=4,
            ),
        )
    )
    # Bubble size is set to liquid variation
    plot.add_trace(
        go.Scatter(
            visible=False,
            x=plot_df["liquid_average"],
            y=plot_df["dried_average"],
            mode="markers",
            marker=dict(
                size=plot_df["liquid_variation"].values.tolist(),
                sizemode="area",
                # Calculate max size of bubble. From: https://plotly.com/python/bubble-charts/#scaling-the-size-of-bubble-charts
                sizeref=2.0 * plot_df["liquid_variation"].max() / (40.0**2),
                sizemin=4,
            ),
        )
    )
    # Bubble size is set to average variation
    plot.add_trace(
        go.Scatter(
            visible=False,
            x=plot_df["liquid_average"],
            y=plot_df["dried_average"],
            mode="markers",
            marker=dict(
                size=plot_df["average_variation"].values.tolist(),
                sizemode="area",
                # Calculate max size of bubble. From: https://plotly.com/python/bubble-charts/#scaling-the-size-of-bubble-charts
                sizeref=2.0 * plot_df["average_variation"].max() / (40.0**2),
                sizemin=4,
            ),
        )
    )

    # Add trendline
    # Exclude Albumin from this calculation because it is a very large outlier
    plot.add_trace(
        go.Scatter(
            x=plot_df["liquid_average"].loc[plot_df["gene_name"] != "ALB"],
            y=trendline.linear_fit,
            name="Linear Regression",
            mode="lines",
            marker=dict(color="red"),
            hoverinfo="skip",
        )
    )

    # Set hover template for all traces in figure
    plot.update_traces(
        # Only select graphs that contain points, exclude trendline
        selector={"mode": "markers"},
        name="Variation",
        mode="markers",
        error_x=dict(type="data", array=plot_df["dried_variation"], visible=True),
        error_y=dict(type="data", array=plot_df["liquid_variation"], visible=True),
        customdata=plot_df[
            [
                "gene_name",
                "protein_id",
                "average_variation",
            ]
        ],
        hovertemplate="<br>".join(
            [
                "Gene Name: %{customdata[0]}",
                "Dried Average: %{x}%",
                "Liquid Average: %{y}%",
                "Average Variation: ± %{customdata[2]}%",
                "<extra></extra>",
            ]
        ),
    )

    # Add buttons to filter through each of the various intensities
    # Dried, Liquid, Average, Trendline
    plot.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="up",
                showactive=True,
                buttons=list(
                    [
                        dict(
                            label="View Dried Variation",
                            method="update",
                            args=[{"visible": [True, False, False, True]}],
                        ),
                        dict(
                            label="View Liquid Variation",
                            method="update",
                            args=[{"visible": [False, True, False, True]}],
                        ),
                        dict(
                            label="View Average Variation",
                            method="update",
                            args=[{"visible": [False, False, True, True]}],
                        ),
                    ]
                ),
            )
        ]
    )

    # Add title and axis labels
    plot.update_layout(title=file_operations.get_experiment_title(input_data))
    plot.update_xaxes(title_text="Dried Average Intensity")
    plot.update_yaxes(title_text="Liquid Average Intensity")

    # Add linear regression equation as an annotation
    regression_equation = "<br>".join(
        [
            f"(Liquid Average) = {trendline.slope:.3f} * (Dried Average) + {trendline.y_intercept:.3e}",
            f"R² = {trendline.r_squared:.3f}",
            f"Unique proteins identified = {len(plot_df['gene_name'].values)}",
        ]
    )
    plot.add_annotation(
        text=regression_equation,
        showarrow=False,
        x=1,
        y=0,
        xref="paper",
        yref="paper",
        align="right",
    )

    # Make buttons to modify graph
    plot.update_layout()

    return plot


def main() -> None:
    try:
        input_file = pathlib.Path(sys.argv[1])
        output_path = input_file.parent

        if input_file.match("proteinGroups.txt"):
            data_frame = create_intensity_dataframe(input_file=input_file)
            data_frame = statistics.calculate_statistics(intensities=data_frame)
            data_frame = filter_values.filter_variation(data_frame)
            data_frame = filter_values.filter_clinically_relevant(data_frame)

            plot = make_plot(intensities=data_frame, input_data=input_file)
            file_operations.write_intensities(
                data_frame=data_frame, output_path=output_path
            )
            file_operations.write_plot_to_file(plot, output_path)

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
