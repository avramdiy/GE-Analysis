from flask import Flask, render_template_string, send_file, abort
import pandas as pd
from pathlib import Path

app = Flask(__name__)

# Locate the data file relative to the repository root
DATA_PATH = Path(__file__).resolve().parents[1] / "ge.us.txt"


def load_data():
    """Load `ge.us.txt` into a pandas DataFrame.

    - Parses the `Date` column as datetimes when present.
    - Drops `OpenInt` if present (added for 2nd commit requirement).
    """
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    # Read once and handle Date parsing explicitly
    df = pd.read_csv(DATA_PATH)
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    # Drop OpenInt column if present
    if "OpenInt" in df.columns:
        df = df.drop(columns=["OpenInt"])

    return df


def split_timeframes(df):
    """Create three dataframes split by logical timeframes.

    Reasoning for splits:
    - Early period: 1962-01-02 through 1989-12-31 — captures the first ~28 years of historical pricing.
    - Mid period: 1990-01-01 through 2004-12-31 — covers market structure changes and the dot-com era.
    - Recent period: 2005-01-01 through 2017-11-10 — final span in the file including post-2008 recovery.

    Returns a dict with keys `master`, `early`, `mid`, `recent`.
    """
    if "Date" not in df.columns:
        # If no Date column, return master only (duplicate for others)
        return {"master": df, "early": df.copy(), "mid": df.copy(), "recent": df.copy()}

    early_start = pd.Timestamp("1962-01-02")
    early_end = pd.Timestamp("1989-12-31")
    mid_start = pd.Timestamp("1990-01-01")
    mid_end = pd.Timestamp("2004-12-31")
    recent_start = pd.Timestamp("2005-01-01")
    recent_end = pd.Timestamp("2017-11-10")

    df_early = df[(df["Date"] >= early_start) & (df["Date"] <= early_end)].copy()
    df_mid = df[(df["Date"] >= mid_start) & (df["Date"] <= mid_end)].copy()
    df_recent = df[(df["Date"] >= recent_start) & (df["Date"] <= recent_end)].copy()

    return {"master": df, "early": df_early, "mid": df_mid, "recent": df_recent}


# Precompute time-sliced DataFrames for convenient access
TIMEFRAMES = split_timeframes(load_data())


@app.route("/")
def index():
    """Render an HTML page with the dataframe (first 100 rows)."""
    df = TIMEFRAMES.get("master")
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
      <p>Displaying the first 100 rows. Use <a href="/all">/all</a> to view full table, <a href="/timeframes">/timeframes</a> to see timeframe counts, or <a href="/download">download</a> the raw file.</p>
      {{ table | safe }}
    </div>
  </body>
</html>"""
    )
    return render_template_string(template, table=html_table)


@app.route("/all")
def all_table():
    """Return the full dataframe as HTML (use with caution for very large files)."""
    df = TIMEFRAMES.get("master")
    return df.to_html(classes="table table-sm", index=False)


@app.route("/timeframes")
def timeframes_summary():
    """Return a small HTML summary showing counts for each timeframe DataFrame."""
    tf = TIMEFRAMES
    rows = {
        "master": len(tf.get("master")),
        "early (1962-1989)": len(tf.get("early")),
        "mid (1990-2004)": len(tf.get("mid")),
        "recent (2005-2017)": len(tf.get("recent")),
    }
    html = "<h2>Timeframe row counts</h2><ul>"
    for k, v in rows.items():
        html += f"<li><strong>{k}</strong>: {v} rows</li>"
    html += "</ul>"
    return render_template_string(html)


@app.route("/download")
def download():
    """Send the raw data file for download."""
    try:
        return send_file(DATA_PATH, as_attachment=True)
    except Exception:
        abort(404)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

