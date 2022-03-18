import argparse

import pandas as pd
import plotly
import plotly.graph_objects as go

import file_operations
import statistics


def create_abundance_values(
    original_df: pd.DataFrame, remove_albumin: bool = True
) -> pd.DataFrame:

    if remove_albumin:
        # Need to use '.copy()' otherwise Pandas is angry that we are changing values of the original dataframe
        # From: https://stackoverflow.com/questions/59821468/
        data_frame: pd.DataFrame = original_df[original_df["gene_name"] != "ALB"].copy()
    else:
        data_frame: pd.DataFrame = original_df.copy()

    # Set expected_concentration to float values
    data_frame["expected_concentration"] = data_frame["expected_concentration"].astype(
        float
    )

    # Filter by expected concentration
    data_frame = data_frame.sort_values(
        "expected_concentration", ascending=False, ignore_index=True
    )

    # Create a ranked index
    data_frame["rank"] = data_frame["expected_concentration"].rank(
        method="first",
        na_option="bottom",
        ascending=False,
    )

    # Remove values with unknown concentration
    data_frame = data_frame[(data_frame["expected_concentration"] >= 0)]
    return data_frame


def abundance_vs_lfq_intensity(
    data_frame: pd.DataFrame, args: argparse.Namespace
) -> plotly.graph_objects.Figure:
    """
    This function will be responsible for creating an Abundance vs LFQ Intensity plot
    Abundnace will be on the x-axis, and LFQ Intensity will be on the y-axis

    :param data_frame: The dataframe containing intensities, averages, etc.
    :param args: The obtained command line arguments
    :return:
    """
    abundance_frame: pd.DataFrame = create_abundance_values(data_frame)
    plot_df: pd.DataFrame = abundance_frame[abundance_frame["relevant"]]

    # Create the scatter plot
    # Intensity is set to dried average
    plot = go.Figure()
    plot.add_trace(
        go.Scatter(
            visible=True,
            x=plot_df["rank"],
            y=plot_df["dried_average"],
            mode="markers",
            customdata=plot_df[["gene_name"]],
            hovertemplate="<br>".join(
                [
                    "Gene Name: %{customdata[0]}",
                    "Abundance Rank: %{x}",
                    "Dried Intensity: %{y}",
                    "<extra></extra>",
                ]
            ),
        ),
    )

    # Intensity is set to liquid average
    plot.add_trace(
        go.Scatter(
            visible=False,
            x=plot_df["rank"],
            y=plot_df["liquid_average"],
            mode="markers",
            customdata=plot_df[["gene_name"]],
            hovertemplate="<br>".join(
                [
                    "Gene Name: %{customdata[0]}",
                    "Abundance Rank: %{x}",
                    "Liquid Intensity: %{y}",
                    "<extra></extra>",
                ]
            ),
        )
    )

    # Intensity is set to average intensity
    plot.add_trace(
        go.Scatter(
            visible=False,
            x=plot_df["rank"],
            y=plot_df["average_intensity"],
            mode="markers",
            customdata=plot_df[["gene_name"]],
            hovertemplate="<br>".join(
                [
                    "Gene name: %{customdata}",
                    "Abundance Rank: %{x}",
                    "Average Intensity: %{y}",
                    "<extra></extra>",
                ]
            ),
        )
    )

    # Add buttons to filter through each of the various intensities
    # Dried, Liquid, Average is order of True/False values
    plot.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="up",
                showactive=True,
                buttons=list(
                    [
                        dict(
                            label="View Dried Intensity",
                            method="update",
                            args=[
                                {"visible": [True, False, False]},
                                {"yaxis": {"title": "Dried Intensity"}},
                            ],
                        ),
                        dict(
                            label="View Liquid Intensity",
                            method="update",
                            args=[
                                {"visible": [False, True, False]},
                                {"yaxis": {"title": "Liquid Intensity"}},
                            ],
                        ),
                        dict(
                            label="View Average Intensity",
                            method="update",
                            args=[
                                {"visible": [False, False, True]},
                                {"yaxis": {"title": "Average Intensity"}},
                            ],
                        ),
                    ]
                ),
            )
        ]
    )

    # TODO: This needs to be finished
    # Add buttons for switching between average, dried, and liquid intensity?
    plot.update_layout(title="Without Albumin Data")
    plot.update_xaxes(title_text="Abundance Rank")
    plot.update_yaxes(title_text="Dried Intensity")

    # plot.write_html("/Users/joshl/Downloads/without_albumin.html")
    plot.show()

    return plotly.graph_objects.Figure()


# Variation (y) vs Abundance rank (x) graph
def abundance_vs_variation(data_frame: pd.DataFrame, args: argparse.Namespace):
    """
    This function will be responsible for creating an Abundance vs Variation plot
    Abundance will be on the x-axis and Variation will be on the y-axis

    :param data_frame: The dataframe containing intensities, averages, etc.
    :param args: The obtained command line arguments
    :return:
    """
    # TODO: Start and finish this graph
    return plotly.graph_objects.Figure()


def liquid_intensity_vs_dried_intensity(
    data_frame: pd.DataFrame,
    args: argparse.Namespace,
) -> plotly.graph_objects.Figure:
    """
    This function is responsible for creating the final Plotly graph


    :param data_frame: The dataframe containing intensity values from MaxQuant
    :param args: Command line arguments retrieved from arg_parse.py
    :return: A plotly.graph_objects.Figure
    """

    # Create a new dataframe to filter the values we need
    # Only take clinically relevant proteins
    plot_df: pd.DataFrame = data_frame[data_frame["relevant"]]

    # Only take the first majority protein ID
    plot_df = plot_df.assign(
        majority_id=plot_df["protein_id"].str.split(";", expand=True, n=1)[0]
    )

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
                sizeref=2.0 * plot_df["average_variation"].max() / (40.0**2),
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
                sizeref=2.0 * plot_df["average_variation"].max() / (40.0**2),
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
        error_x=dict(type="data", array=plot_df["liquid_variation"], visible=True),
        error_y=dict(type="data", array=plot_df["dried_variation"], visible=True),
        customdata=plot_df[
            [
                "gene_name",
                "majority_id",
                "average_variation",
            ]
        ],
        hovertemplate="<br>".join(
            [
                "Gene Name: %{customdata[0]}",
                "Majority Protein ID: %{customdata[1]}",
                "Dried Average: %{y}%",
                "Liquid Average: %{x}%",
                "Average Variation: ± %{customdata[2]}%",
                "<extra></extra>",
            ]
        ),
    )

    # Add buttons to filter through each of the various intensities
    # Dried, Liquid, Average, Trendline is order of True/False values
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
    plot.update_layout(title=file_operations.get_experiment_title(args))
    plot.update_xaxes(title_text="Liquid Average Intensity")
    plot.update_yaxes(title_text="Dried Average Intensity")

    # Add linear regression equation as an annotation
    regression_equation = "<br>".join(
        [
            f"(Dried Average) = {trendline.slope:.3f} * (Liquid Average) + {trendline.y_intercept:.3e}",
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

    return plot
