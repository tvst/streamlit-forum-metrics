from urllib.parse import urljoin, urlencode
import datetime
import pytz

import pandas as pd
import requests

import streamlit as st


BASE_URL = 'https://discuss.streamlit.io'
TTL = 60 * 60  # 1 hour


@st.cache(ttl=TTL, show_spinner=False)
def fetch(path, **query):
    url = urljoin(BASE_URL, path)
    if query:
        query_str = urlencode(query)
        url = "%s?%s" % (url, query_str)
    return requests.get(url)


@st.cache(ttl=TTL, show_spinner=False)
def fetch_categories():
    resp = fetch('categories.json')
    data = resp.json()
    cat_data = data['category_list']['categories']
    table = get_categories_as_table(cat_data)
    table.set_index('name', inplace=True)
    return table


@st.cache(ttl=TTL, show_spinner=False)
def fetch_categories_dict():
    resp = fetch('categories.json')
    data = resp.json()
    cat_data = data['category_list']['categories']
    return get_categories_as_dict(cat_data)


@st.cache(ttl=TTL, show_spinner=False)
def fetch_page_of_latest_posts(page=0):
    resp = fetch('posts.json', page=page)
    data = resp.json()
    post_data = data['latest_posts']
    return get_post_data_as_table(post_data)


@st.cache(ttl=TTL, show_spinner=False)
def fetch_page_of_latest_topics(page=0):
    resp = fetch('latest.json', page=page)
    data = resp.json()
    topics_data = data['topic_list']['topics']
    return get_topics_data_as_table(topics_data)


@st.cache(ttl=TTL, show_spinner=False)
def fetch_latest_topics_by_timedelta(**kwargs):
    now = datetime.datetime.now(tz=pytz.UTC)
    timedelta = datetime.timedelta(**kwargs)
    threshold_date = now - timedelta

    posts_list = []
    page = 0

    while True:
        batched_posts = fetch_page_of_latest_topics(page)

        # Remove posts more than 7 days old.
        batched_posts = batched_posts.loc[
            batched_posts['last_posted_at'] > threshold_date]

        if batched_posts.empty:
            break

        posts_list.append(batched_posts)
        page += 1

    return pd.concat(posts_list)


@st.cache(ttl=TTL, show_spinner=False)
def get_categories_as_table(cat_data):
    table = pd.DataFrame(cat_data)
    return table[[
        'id',
        'name',
        'topic_count',
        'post_count',
        'topics_day',
        'topics_week',
        'topics_month',
        'topics_year',
        'topics_all_time',
    ]]


@st.cache(ttl=TTL, show_spinner=False)
def get_categories_as_dict(cat_data):
    return {d['id']: d['name'] for d in cat_data}


@st.cache(ttl=TTL, show_spinner=False)
def get_post_data_as_table(post_data):
    table = pd.DataFrame(post_data)
    table['created_at'] = pd.to_datetime(table['created_at'])
    return table[[
        'id',
        'display_username',
        'created_at',
        'raw',
        'staff',
        'reads',
        'post_number',
    ]]


@st.cache(ttl=TTL, show_spinner=False)
def get_topics_data_as_table(topics_data):
    table = pd.DataFrame(topics_data)
    table['created_at'] = pd.to_datetime(table['created_at'])
    table['last_posted_at'] = pd.to_datetime(table['last_posted_at'])

    categories = fetch_categories_dict()
    table['category'] = table['category_id'].map(categories)

    return table[[
        'title',
        'last_posted_at',
        'created_at',
        'category',
        'views',
        'posts_count',
        'like_count',
    ]]


@st.cache(ttl=TTL, show_spinner=False)
@st.cache(show_spinner=False)
def to_date(json_date):
    if json_date.endswith('Z'):
        json_date = json_date[:-1]
    return datetime.datetime.fromisoformat(json_date)
