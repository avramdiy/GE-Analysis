# TRG Week 52

## $GE (General Electric)

- Diversified industrial conglomerate — leading aerospace, power and renewable-energy businesses — shifting toward higher-margin aviation and clean-energy segments; cyclical revenue with focus on cash-generation and debt reduction.

- https://www.kaggle.com/borismarjanovic/datasets

### 1st Commit

- Added `app/data.py`: Flask API that loads `ge.us.txt` and serves the data as an HTML dataframe (routes: `/` preview, `/all` full table, `/download` raw file). Added `requirements.txt` listing `flask` and `pandas`.

### 2nd Commit

- Dropped `OpenInt` from the master DataFrame and created three time-sliced DataFrames (`early` 1962–1989, `mid` 1990–2004, `recent` 2005–2017) available in `app/data.py` via the `TIMEFRAMES` dictionary.

### 3rd Commit

- Added `/correlations` route to visualize correlation heatmaps for each timeframe (early, mid, recent). Heatmaps are generated using seaborn/matplotlib and embedded as base64 images in HTML. Updated `requirements.txt` to include `matplotlib` and `seaborn`.

### 4th Commit

### 5th Commit