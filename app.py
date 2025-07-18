import datetime
import os

import matplotlib.pyplot as plt
import pandas as pd
import praw
import seaborn as sns
import statsd
import stqdm
import streamlit as st
from transformers import pipeline


@st.cache_data
def get_classifer():
    return pipeline(
        "text-classification",
        model="bhadresh-savani/albert-base-v2-emotion",
        return_all_scores=True,
    )


def auth_reddit():
    return praw.Reddit(
        client_id=os.environ.get("CLIENT_ID"),
        client_secret=os.environ.get("CLIENT_SECRET"),
        username=os.environ.get("USERNAME"),
        password=os.environ.get("PASSWORD"),
        user_agent=os.environ.get("USER_AGENT"),
    )


pipe = get_classifer()
reddit = auth_reddit()
stats = statsd.StatsClient("graphite", 8125)

subreddit_name = st.text_input("Enter subreddit name", "memes")
time_filter = st.selectbox("Select time filter", ["day", "week", "month"])
limit = st.slider("Select number of posts", 1, 200, 10)


@st.cache_data
def get_top_posts(subreddit_name, time_filter, limit) -> pd.DataFrame:

    df = pd.DataFrame(columns=["Title", "Created", "Content", "Score", "Comments"])

    try:
        stats.incr("reddit_api.request")
        subreddit = reddit.subreddit(subreddit_name)

        for post in subreddit.top(time_filter, limit=limit):
            stats.incr("reddit_api.post")
            df.loc[len(df)] = [
                post.title,
                post.created_utc,
                post.selftext,
                post.score,
                post.num_comments,
            ]

        df["Created"] = df["Created"].apply(
            lambda x: datetime.datetime.utcfromtimestamp(x)
        )

        return df

    except:
        st.write(f"Subreddit {subreddit_name} does not exist")
        st.stop()


@stats.timer("sentiment_analysis.run_time")
def get_sentiment(posts: pd.DataFrame):
    emotions = ["joy", "anger", "love", "sadness", "fear", "surprise"]

    df_emotios = pd.DataFrame(columns=emotions)
    for post in stqdm.stqdm(posts.itertuples(), total=posts.shape[0]):
        result = pipe(post.Title)[0]
        result = {emotion["label"]: emotion["score"] for emotion in result}
        df_emotios.loc[len(df_emotios)] = result

    df_emotios["date"] = posts["Created"].dt.date
    df_emotios["hour"] = posts["Created"].dt.hour

    return df_emotios


def plot_number_of_posts(posts: pd.DataFrame):
    st.header(f"Number of post in selected time: {posts.shape[0]}")
    fig = plt.figure(figsize=(15, 8))

    if time_filter == "day":
        sns.histplot(posts["Created"].dt.hour)
        plt.xlabel("Time [hours]")
    else:
        sns.histplot(posts["Created"].dt.date)
        plt.xlabel("Time [days]")

    plt.ylabel("Number of posts")
    plt.title("Number of posts over time")
    st.pyplot(fig)


def plot_general_emotions(sentiments: pd.DataFrame):
    st.header("General emotions in posts")
    fig = plt.figure(figsize=(15, 8))

    sentiments = sentiments.drop(columns=["date", "hour"])
    sns.boxplot(data=sentiments)

    plt.xlabel("Emotion")
    plt.ylabel("Score")
    plt.title("General emotions in posts")
    st.pyplot(fig)


def plot_emotions_over_time(sentiments: pd.DataFrame):
    st.header("Emotions over time")
    fig = plt.figure(figsize=(15, 8))

    sentiments = sentiments.melt(
        id_vars=["date"], value_vars=sentiments.columns.drop(["hour", "date"])
    )
    sns.lineplot(data=sentiments, x="date", y="value", hue="variable")

    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.title("Emotions over time")
    st.pyplot(fig)


def plot_emotions_over_time_hourly(sentiments: pd.DataFrame):
    st.header("Emotions over time hourly")
    fig = plt.figure(figsize=(15, 8))

    sentiments = sentiments.melt(
        id_vars=["hour"], value_vars=sentiments.columns.drop(["hour", "date"])
    )
    sns.lineplot(data=sentiments, x="hour", y="value", hue="variable")

    plt.xlabel("Time")
    plt.ylabel("Score")
    plt.title("Emotions over time hourly")
    st.pyplot(fig)


def plot_score_on_emotions(sentiments: pd.DataFrame, posts: pd.DataFrame):
    st.header("Score on emotions")
    fig = plt.figure(figsize=(15, 8))

    _sentiments = pd.concat([sentiments, posts["Score"]], axis=1)
    _sentiments = _sentiments.melt(
        id_vars=["Score"], value_vars=_sentiments.columns.drop(["hour", "date"])
    )
    sns.scatterplot(data=_sentiments, x="Score", y="value", hue="variable")

    plt.xlabel("Score")
    plt.ylabel("Emotion")
    plt.title("Score on emotions")
    st.pyplot(fig)


def plot_num_comments_on_emotions(sentiments: pd.DataFrame, posts: pd.DataFrame):
    st.header("Number of comments on emotions")
    fig = plt.figure(figsize=(15, 8))

    _sentiments = pd.concat([sentiments, posts["Comments"]], axis=1)
    _sentiments = _sentiments.melt(
        id_vars=["Comments"], value_vars=_sentiments.columns.drop(["hour", "date"])
    )
    sns.scatterplot(data=_sentiments, x="Comments", y="value", hue="variable")

    plt.xlabel("Comments")
    plt.ylabel("Emotion")
    plt.title("Number of comments on emotions")
    st.pyplot(fig)


posts = get_top_posts(subreddit_name, time_filter, limit)
sentiments = get_sentiment(posts)

plot_number_of_posts(posts)
plot_general_emotions(sentiments)
plot_emotions_over_time(sentiments)
plot_emotions_over_time_hourly(sentiments)
plot_score_on_emotions(sentiments, posts)
plot_num_comments_on_emotions(sentiments, posts)
