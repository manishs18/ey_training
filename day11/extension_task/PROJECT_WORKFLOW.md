# Day 11 Extension Task Workflow

This file explains the time-series EDA pipeline in simple step-by-step form.

## What this project does

The project reads the Sakshi PPG time-series dataset, cleans missing values, creates time-based features, runs time-series analysis, and saves charts plus reports.

## Folder structure

```text
extension_task/
  data/
    sakshi_audio_20260611T074737_len148s.wav
    sakshi_imu_20260611T074737_len148s.csv
    sakshi_ppg_20260611T074737_len148s.csv
    sakshi_rr_intervals_20260611T074737_len128s.csv
  decomposition/
    trend.csv
    seasonal.csv
    residual.csv
    decomposition.png
  plots/
    time_series.png
    acf.png
    pacf.png
    monthly_boxplot.png
    weekly_boxplot.png
  reports/
    missing_values_report.csv
    summary_statistics.csv
    feature_engineering_report.csv
    stationarity_report.txt
  src/
    config.py
    data_loader.py
    eda.py
    feature_engineering.py
    time_series_analysis.py
    main.py
  requirements.txt
  README.md
```

## Why these files are used

- `config.py` keeps paths and column names in one place so the pipeline is easy to change.
- `data_loader.py` keeps CSV loading separate from analysis logic.
- `eda.py` calculates missing-value and summary reports.
- `feature_engineering.py` adds useful time-series features such as lag, rolling mean, and differencing.
- `time_series_analysis.py` handles plots, decomposition, stationarity testing, and autocorrelation analysis.
- `main.py` connects every step in the correct order.

## Step-by-step workflow

1. `main.py` creates output folders if they do not already exist.
2. The CSV file is loaded from `data/` using `load_data()`.
3. The timestamp column is converted to datetime and the data is sorted.
4. The timestamp column becomes the index so time-based operations work correctly.
5. `missing_report()` generates a missing-value summary and saves it in `reports/`.
6. Missing values are filled using forward fill and backward fill.
7. `summary_stats()` computes basic statistics such as mean, median, min, max, and mode.
8. `create_features()` adds hour, day, month, weekday, lag values, rolling statistics, and difference features.
9. `plot_series()` saves the main time-series chart in `plots/`.
10. `boxplots()` creates monthly and weekly boxplots.
11. `decompose_series()` splits the signal into trend, seasonal, and residual parts and saves both CSV and image output.
12. `stationarity_test()` runs the Augmented Dickey-Fuller test and writes the result to a text file.
13. `plot_acf_pacf()` saves ACF and PACF plots for autocorrelation analysis.

## Workflow diagram

```mermaid
flowchart TD
    A[CSV files in data/] --> B[load_data()]
    B --> C[Convert timestamp to datetime]
    C --> D[Sort data and set index]
    D --> E[missing_report()]
    E --> F[Fill missing values]
    F --> G[summary_stats()]
    G --> H[create_features()]
    H --> I[plot_series()]
    H --> J[boxplots()]
    H --> K[decompose_series()]
    H --> L[stationarity_test()]
    H --> M[plot_acf_pacf()]
    I --> N[plots/]
    J --> N
    K --> O[decomposition/]
    L --> P[reports/]
    M --> N
```

## Why this approach is useful

- Time-series data must be sorted and indexed by time before rolling or lag features work properly.
- Missing-value handling is needed before statistical tests and decomposition.
- Lag and rolling features help reveal patterns that are not visible in raw values.
- ADF, ACF, and PACF are used because they are standard tools for checking stationarity and autocorrelation.
- Decomposition helps separate the signal into trend, seasonality, and noise.

## Output insight

After the run, you get a complete EDA package:

- data quality report
- summary statistics
- engineered features report
- time-series charts
- decomposition outputs
- stationarity result

This means the project is not training a predictive model yet. It is preparing the dataset and giving a clear analysis of the signal first.