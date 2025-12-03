from flask import Flask, render_template_string, send_file, abort
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# Locate the data file relative to the repository root
DATA_PATH = Path(__file__).resolve().parents[1] / "ge.us.txt"


def load_data():
		"""Load `ge.us.txt` into a pandas DataFrame.

		Parses the `Date` column as datetimes when present.
		"""
		if not DATA_PATH.exists():
				raise FileNotFoundError(f"Data file not found: {DATA_PATH}")
		df = pd.read_csv(DATA_PATH, parse_dates=["Date"]) if "Date" in pd.read_csv(DATA_PATH, nrows=0).columns else pd.read_csv(DATA_PATH)
		return df


@app.route("/")
def index():
		"""Render an HTML page with the dataframe (first 100 rows)."""
		df = load_data()
		html_table = df.head(100).to_html(classes="table table-striped", index=False)
		template = (
				"""<!doctype html>
<html>
	<head>
		<meta charset="utf-8">
		<meta name="viewport" content="width=device-width, initial-scale=1">
		<title>GE Data</title>
		<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
	</head>
	<body class="p-4">
		<div class="container">
			<h1>GE Price Data (`ge.us.txt`)</h1>
			<p>Displaying the first 100 rows. Use <a href="/all">/all</a> to view full table or <a href="/download">download</a> the raw file.</p>
			{{ table | safe }}
		</div>
	</body>
</html>"""
		)
		return render_template_string(template, table=html_table)


@app.route("/all")
def all_table():
		"""Return the full dataframe as HTML (use with caution for very large files)."""
		df = load_data()
		return df.to_html(classes="table table-sm", index=False)


@app.route("/download")
def download():
		"""Send the raw data file for download."""
		try:
				return send_file(DATA_PATH, as_attachment=True)
		except Exception:
				abort(404)


if __name__ == "__main__":
		app.run(debug=True, host="0.0.0.0", port=5000)

