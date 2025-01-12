import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import base64
from flask import Flask, render_template, request, jsonify
from io import BytesIO
from matplotlib.colors import LinearSegmentedColormap

app = Flask(__name__)

# Available color schemes for Seaborn (defined as a constant)
COLOR_SCHEMES = [
    "Blues", "BuGn", "BuPu", "GnBu", "Greens", "Greys", "Oranges", "OrRd", "Purples", 
    "PuBu", "PuBuGn", "PuOr", "PuRd", "RdBu", "RdGy", "RdPu", "RdYlBu", "RdYlGn", "YlGn", 
    "YlGnBu", "YlOrBr", "YlOrRd", "coolwarm", "viridis", "magma", "inferno", "cividis", 
    "twilight", "twilight_shifted"
]

def generate_colormap(color_scheme, custom_colors):
    """Generate a colormap based on the selected scheme or custom colors."""
    if color_scheme.startswith("custom_"):
        return LinearSegmentedColormap.from_list("custom_gradient", custom_colors)
    return color_scheme

@app.route("/")
def home():
    return render_template("index.html", heatmap_generated=False, color_schemes=COLOR_SCHEMES)

@app.route("/api/generate-heatmap", methods=["POST"])
def generate_heatmap():
    if request.method == "POST":
        try:
            # Retrieving and validating the form data
            uploaded_file = request.files.get("file")
            if not uploaded_file or uploaded_file.filename == "":
                raise ValueError("No file selected")

            file_content = uploaded_file.read()
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

            # Handle custom color schemes
            if color_scheme.startswith("custom_"):
                custom_colors = [
                    request.form["custom_color1"], 
                    request.form["custom_color2"], 
                    request.form.get("custom_color3")
                ]
                custom_colors = [c for c in custom_colors if c]  # Remove None or empty values
                cmap = generate_colormap(color_scheme, custom_colors)
            else:
                cmap = color_scheme

            # Read and preprocess the data
            df = pd.read_excel(file_content, sheet_name=sheet_number - 1, header=start_row - 1)
            df = df.iloc[:, start_col - 1:]
            df.set_index(df.columns[0], inplace=True)

            # Generate the heatmap
            fig, ax = plt.subplots(figsize=(width, height))
            sns.heatmap(
                df, annot=annotations, fmt=".2f", linewidths=line_width,
                cmap=cmap, ax=ax, cbar_kws={"aspect": 70}
            )
            plt.title(plot_title, fontsize=font_size)
            plt.tight_layout()

            # Save the plot to a BytesIO object and convert to base64
            img = BytesIO()
            plt.savefig(img, format="png")
            img.seek(0)
            plt.close()

            img_base64 = base64.b64encode(img.read()).decode("utf-8")

            return jsonify({
                "heatmap_generated": True,
                "heatmap_image_url": f'data:image/png;base64,{img_base64}',
                "error": None
            })

        except Exception as e:
            return jsonify({
                "heatmap_generated": False,
                "image": None,
                "error": str(e)
            })

    return jsonify({
        "heatmap_generated": False,
        "image": None,
        "error": "Invalid request method"
    })

if __name__ == "__main__":
    # Run the app with debug mode off (debug=False) and specify host and port
    app.run(debug=False, host='0.0.0.0', port=5000)
