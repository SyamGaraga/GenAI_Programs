📊 YouTube & News Analytics Project

A complete data engineering + analytics project built using **Databricks**, **GNews API**, **YouTube API**, and **Bronze–Silver–Gold Architecture** to analyze news trends and YouTube channel engagement.
This project performs **data ingestion, cleaning, dimensional modeling, sentiment analysis, and visualization** using Databricks notebooks.

## 📁 Project Structure (Medallion Architecture)
YouTube-News-Analytics/
│
├── Bronze/
│   ├── youtube_raw.json
│   ├── news_raw.json
│   └── ...
│
├── Silver/
│   ├── youtube_cleaned.csv
│   ├── news_cleaned.csv
│   └── ...
│
├── Gold/
│   ├── dim_video.csv
│   ├── dim_channel.csv
│   ├── dim_source.csv
│   ├── dim_date.csv
│   ├── fact_comments.csv
│   ├── fact_news.csv
│   └── ...
│
├── Visualizations/
│   ├── top_sources.png
│   ├── view_trends.png
│   ├── sentiment_distribution.png
│   └── ...
│
└── Notebooks/
    ├── ingestion_youtube.ipynb
    ├── ingestion_news.ipynb
    ├── silver_cleaning.ipynb
    ├── gold_dim_fact.ipynb
    └── visualization.ipynb

 🚀 Project Overview

This project builds an end-to-end analytics pipeline using **Databricks** to perform:

 ✔ YouTube Analytics

* Top videos
* Engagement trends

 likes, comments, views
* Sentiment analysis of comments
* Comment patterns and user engagement
* Channel performance

✔ News Analytics

* Top news sources
* Daily reporting patterns
* Most covered topics
* Sentiment analysis of news titles
* Trend analysis over time

🛠 Tech Stack

| Layer                  | Tools Used                        |
| ---------------------- | --------------------------------- |
| **Data Ingestion**     | GNews API, YouTube Data API v3    |
| **Compute**            | Databricks Runtime (Python)       |
| **Storage**            | DBFS (Bronze/Silver/Gold folders) |
| **Data Processing**    | PySpark, Pandas                   |
| **Visualization**      | Matplotlib, Databricks Dashboard  |
| **Sentiment Analysis** | TextBlob / VADER                  |
| **Version Control**    | GitHub                            |



🏗 Architecture Explanation

🔶 Bronze Layer – Raw Data

* Stores **raw API response**
* No cleaning
* Used for reproducibility

Examples:

 youtube_raw.json
 news_raw.json


🔷 Silver Layer – Cleaned Data

Cleaning includes:

* Date formatting
* Null handling
* Removing HTML tags
* Selecting required fields

Output:

youtube_cleaned.csv
news_cleaned.csv

🟡 Gold Layer – Analytics/Dimensional Tables

Created Star Schema:

📌 Dimensions

 dim_video
 dim_channel
 dim_source
 dim_date

📌 Fact Tables

  fact_comments (YouTube)
  fact_news (News articles)

These tables enable BI dashboards & analytics.



📈 Visualizations Included

 YouTube Visuals

* Top 10 viewed videos
* View trends per day
* Like vs View ratio
* Comment distribution
* Sentiment distribution

 News Visuals

* Top news sources
* Publishing trends
* Category analysis


All saved in **/Visualizations folder**.

📌 Future Enhancements

* Real-time pipeline using streaming API
* Power BI / Tableau dashboards
* Topic modeling (LDA)
* ML-based prediction of video popularity

