import statistics

import pandas as pd
import pathlib
import plotly
import plotly.graph_objects as go


def abundance_vs_lfq_intensity():
    """
    This function will be responsible for creating an Abundance vs LFQ Intensity plot
    Abundnace will be on the x-axis, and LFQ Intensity will be on the y-axis
    :return:
    """


def liquid_intensity_vs_dried_intensity(
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
                "protein_id",
                "average_variation",
            ]
        ],
        hovertemplate="<br>".join(
            [
                "Gene Name: %{customdata[0]}",
                "Dried Average: %{y}%",
                "Liquid Average: %{x}%",
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

    print(plot_df.loc[plot_df["gene_name"] == "F10"])

    return plot
