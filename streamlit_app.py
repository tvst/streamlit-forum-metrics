import altair as alt
import streamlit as st

import discourse_api


"""
# 🗨️ Streamlit forums stats
"""

"""
&nbsp;

## Forums categories
"""

categories = discourse_api.fetch_categories()

st.table(categories.T)


"""
&nbsp;

## Most-recently-updated topics
"""

days = st.selectbox(
    'How many days to look back',
    [1, 7, 10, 14, 21, 28, 30, 60, 90],
    1)

raw_topics = discourse_api.fetch_latest_topics_by_timedelta(days=days)

if st.checkbox("Show raw topics"):
    st.dataframe(raw_topics)

# Only keep the data we'll use below, to reduce amount of data sent to the
# browser via Altair
topics = raw_topics[[
    'last_posted_at',
    'created_at',
    'category',
    'views',
    'posts_count',
    'like_count',
]]

categories_list = [None] + list(discourse_api.fetch_categories_dict().values())
input_dropdown = alt.binding_select(options=categories_list)
cat_selection =  alt.selection_single(
    fields=['category'], bind=input_dropdown, name='filter by')


"""
&nbsp;

### Binned by last post date
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='monthdate(last_posted_at):T',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by last post hour
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='hours(last_posted_at):O',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by last post day-of-week
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='day(last_posted_at):O',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by creation date
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='yearmonthdate(created_at):T',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by creation hour
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='hours(created_at):O',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by creation day-of-week
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='day(created_at):O',
        y='count()',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)


"""
&nbsp;

### Binned by category
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x='count()',
        y='category:N',
        color=alt.Color('category', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ),
    use_container_width=True,
)


"""
&nbsp;

### By date and by category
"""

st.altair_chart(alt.Chart(topics)
    .mark_line()
    .encode(
        x='yearmonthdate(last_posted_at):O',
        y='count()',
        color=alt.Color('category:N', legend=alt.Legend(orient='bottom')),
        tooltip='count()',
    ),
    use_container_width=True,
)


"""
&nbsp;

### By likes
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x=alt.X('like_count:Q', bin=alt.Bin(maxbins=20)),
        y='count()',
        tooltip='count()',
    ),
    use_container_width=True,
)


"""
&nbsp;

### By number of posts
"""

st.altair_chart(alt.Chart(topics)
    .mark_bar()
    .encode(
        x=alt.X('posts_count:Q', bin=alt.Bin(maxbins=20)),
        y='count()',
        tooltip='count()',
    ),
    use_container_width=True,
)


"""
&nbsp;

### Relationship between views, posts, and likes
"""

st.altair_chart(alt.Chart(topics)
    .mark_circle()
    .encode(
        x=alt.X('posts_count:Q', scale=alt.Scale(type="log")),
        y=alt.Y('views:Q', scale=alt.Scale(type="log")),
        color=alt.Color('category:N', legend=alt.Legend(orient='bottom')),
        size=alt.Size('sum(like_count)', legend=alt.Legend(orient='bottom')),
    ).add_selection(
        cat_selection
    ).transform_filter(
        cat_selection
    ),
    use_container_width=True,
)
