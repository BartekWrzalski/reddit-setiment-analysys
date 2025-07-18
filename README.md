### Reddit Sentiment Analysis

A Streamlit web application that analyzes emotions in the top posts of a selected subreddit. It uses a transformer-based NLP model for emotion classification and provides insightful data visualizations.


### Features
* Reddit API authentication using PRAW
* Select subreddit, time range, and number of posts to analyze
* Emotion classification in post titles using a transformer model
* Interactive visualizations:
    - Number of posts over time
    - Emotion distribution
    - Emotions over time (by day or hour)
    - Relationship between emotions, upvotes, and comments
* Real-time metrics monitoring with StatsD + Graphite
* Grafana integration for custom dashboards
* Easy deployment via Docker Compose


### Technologies Used
* Python
* Streamlit – web app interface
* PRAW – Reddit API wrapper
* Transformers (HuggingFace) – emotion detection using albert-base-v2-emotion
* Pandas, Matplotlib, Seaborn – data analysis and visualization
* StatsD – metrics collection and monitoring
* Graphite – time-series monitoring backend
* Grafana – interactive dashboards and visualization
* Docker Compose – multi-service orchestration


### Project Setup
You can set up and run the project using either Makefile or Docker Compose.

##### Option 1: Using Makefile (local)
1. Generate the .env file template:
```bash
make env
```
Edit the .env file and add your Reddit API credentials.

2. Create a virtual environment and install dependencies:
```bash
make install
```

3. Activate the virtual environment and run the app:
```bash
make run
```

##### Option 2: Using Docker Compose (with Graphite & Grafana)

1. Generate the .env file template:
```bash
make env
```
Edit the .env file and add your Reddit API credentials.

2. Build and run the app:
```bash
docker-compose up --build
```