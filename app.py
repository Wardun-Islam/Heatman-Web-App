import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from flask import Flask, render_template, request
from io import BytesIO

app = Flask(__name__)

# Available color schemes for Seaborn
color_schemes = [
    "Blues",
    "BuGn",
    "BuPu",
    "GnBu",
    "Greens",
    "Greys",
    "Oranges",
    "OrRd",
    "Purples",
    "PuBu",
    "PuBuGn",
    "PuOr",
    "PuRd",
    "RdBu",
    "RdGy",
    "RdPu",
    "RdYlBu",
    "RdYlGn",
    "YlGn",
    "YlGnBu",
    "YlOrBr",
    "YlOrRd",
    "coolwarm",
    "viridis",
    "magma",
    "inferno",
    "cividis",
    "twilight",
    "twilight_shifted",
]


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Get the uploaded file
            uploaded_file = request.files["file"]
            if uploaded_file.filename == "":
                raise ValueError("No file selected")

            # Read the file content into memory (no saving to disk)
            file_content = uploaded_file.read()

            # User inputs
            sheet_number = int(request.form["sheet_number"])
            start_row = int(request.form["start_row"])
            start_col = int(request.form["start_col"])
            plot_title = request.form["plot_title"]
            color_scheme = request.form["color_scheme"]
            width = float(request.form["width"])
            height = float(request.form["height"])
            font_size = int(request.form["font_size"])
            annotations = request.form["annotations"] == "True"
            line_width = float(request.form["line_width"])

            # Load the Excel file and process the data
            df = pd.read_excel(
                file_content, sheet_name=sheet_number - 1, header=start_row - 1
            )
            df = df.iloc[:, start_col - 1 :]  # Adjust columns
            df.set_index(df.columns[0], inplace=True)

            # Create the plot in memory
            fig, ax = plt.subplots(figsize=(width, height))
            sns.heatmap(
                df,
                annot=annotations,
                fmt=".2f",
                linewidths=line_width,
                cmap=color_scheme,
                ax=ax,
            )
            plt.title(plot_title, fontsize=font_size)
            plt.tight_layout()

            # Save the plot to a BytesIO object
            img = BytesIO()
            plt.savefig(img, format="png")
            img.seek(0)
            plt.close()

            # Convert image to base64
            img_base64 = base64.b64encode(img.read()).decode("utf-8")

            return render_template(
                "index.html",
                heatmap_generated=True,
                img_base64=img_base64,
                color_schemes=color_schemes,
            )

        except Exception as e:
            return render_template(
                "index.html",
                heatmap_generated=False,
                error=str(e),
                color_schemes=color_schemes,
            )

    return render_template(
        "index.html", heatmap_generated=False, error=None, color_schemes=color_schemes
    )


if __name__ == "__main__":
    app.run(debug=True)
