from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter
import emoji

extract = URLExtract()

def fetch_stats(selected_user,df):

    # if selected_user != "Overall":
    #     df = df[df['user'] == selected_user]
    # num_messages = df.shape[0]
    # words = []
    # for message in df['message']:
    #     words.extend(message.split())

    # return num_messages,len(words)

    if selected_user == "Overall":

        num_messages = df.shape[0]


        words = []
        for message in df['message']:
            words.extend(message.split())


        num_media = df[df['message'] == '<Media omitted>\n'].shape[0]


        links = []
        for message in df['message']:
            links.extend(extract.find_urls(message))

        return num_messages, len(words), num_media, len(links)
    else:
        n_df = df[df['user'] == selected_user]
        num_messages = n_df.shape[0]

        words = []
        for message in n_df['message']:
            words.extend(message.split())

        num_media = n_df[n_df['message'] == '<Media omitted>\n'].shape[0]


        links = []
        for message in n_df['message']:
            links.extend(extract.find_urls(message))

        return num_messages, len(words), num_media, len(links)
        # return df[df['user'] == selected_user]

def most_busy_users(df):
    x = df['user'].value_counts().head()
    df = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index().rename(
        columns={'index': 'name', 'user': 'percent'})
    return x, df

def create_word_cloud(selected_user,df):

    f = open('stop_words.txt', 'r')
    stop_words = f.read()
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']

    def remove_stop_words(message):
        y=[]
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    temp['message']=temp['message'].apply(remove_stop_words)
    df_wc = wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user, df):

    f = open('stop_words.txt', 'r')
    stop_words = f.read()
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    temp = df[df['user'] != 'group_notification']
    temp = temp[temp['message'] != '<Media omitted>\n']
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)

    most_common_df = pd.DataFrame(Counter(words).most_common(20))
    return most_common_df

def emoji_helper(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.distinct_emoji_list(message)])

    emoji_df = pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return emoji_df

def monthly_timeline(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))
    timeline['time'] = time
    return timeline

def daily_timeline(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    daily_timeline = df.groupby('only_date').count()['message'].reset_index()
    return  daily_timeline

def weekly_activity_map(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()

def monthly_activity_map(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()

def activity_heatmap(selected_user,df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    user_heatmap = df.pivot_table(index='day_name',columns='period',values='message',aggfunc='count').fillna(0)
    return user_heatmap

def data_range(start_year,end_year,start_month,end_month,df):
    start_year=int(start_year)
    end_year=int(end_year)
    sy = start_year
    ey = end_year
    df1 = df

    y = pd.DataFrame()
    while (True):
        if end_year < start_year:
            break
        else:
            b = df1[df1["year"] == end_year]
            y = pd.concat([y, b])
            end_year -= 1

    m = pd.DataFrame()
    month = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
             'November', 'December']
    start_month_index = month.index(start_month)
    end_month_index = month.index(end_month)
    while (True):
        b = y[(y["year"] == sy) & (df1["month"] == month[start_month_index])]
        m = pd.concat([m, b])
        start_month_index = (start_month_index + 1)
        if start_month_index == 12:
            start_month_index = 0
            sy += 1
        if (start_month_index == end_month_index + 1) and sy == ey:
            break
    return m
