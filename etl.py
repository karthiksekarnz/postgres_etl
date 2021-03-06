import os
import io
import glob
import numpy as np
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
    Description: This function is responsible for extracting the data from song file
    and load them into database tables

    Arguments:
        cur: Cursor object
        filepath: File path of the song data file as a string.

    Returns:
        None
    """
    # open song file
    df = pd.read_json(filepath, typ="Series")

    # insert song record
    song_data = df[["song_id", "title", "artist_id", "year", "duration"]]
    song_data = list(song_data.values)
    cur.execute(song_table_insert, song_data)

    # insert artist record
    artist_data = df[["artist_id", "artist_name", "artist_location", "artist_latitude", "artist_longitude"]]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
        Description: This function is responsible for extracting the data from log files
        and transform the data and persist the song play data into songplays table
        for analysis

        Arguments:
            cur: Cursor object
            filepath: File path of the log data file as a string.

        Returns:
            None
        """
    # open log file
    df = pd.read_json(filepath, lines=True)
    df.fillna(0, inplace=True)

    # filter by NextSong action
    df = df[df["page"] == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df["ts"], unit="ms")

    # insert time data records
    time_data = [t, t.dt.hour, t.dt.day, t.dt.weekofyear, t.dt.month, t.dt.year, t.dt.weekday]
    column_labels = ["start_time", "hour", "day", "weekofyear", "month", "year", "weekday"]
    time_df = pd.DataFrame(dict(zip(column_labels, time_data)))

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = df[["userId", "firstName", "lastName", "gender", "level"]]
    user_df["userId"].replace("", np.NAN).dropna()

    # insert user records
    for i, row in user_df.iterrows():
        if row.userId:
            cur.execute(user_table_insert, row)

    songplay_df = pd.DataFrame()

    for index, row in df.iterrows():
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (str(row.song), str(row.artist), str(row.length)))
        results = cur.fetchone()

        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        ts = pd.to_datetime(row.ts, unit="ms")
        if row.userId:
            songplay_data = pd.Series(
                [ts, row.userId, row.level, songid, artistid, row.sessionId, row.location, row.userAgent], dtype=str)
            songplay_df = songplay_df.append(songplay_data, ignore_index=True)

    # insert songplay records
    str_buffer = io.StringIO()
    songplay_df.to_csv(str_buffer, index=False, header=False, sep="\t")
    str_buffer.seek(0)

    songplay_columns = ("start_time", "user_id", "level", "song_id", "artist_id", "session_id", "location", "user_agent")
    cur.copy_from(str_buffer, "songplays", sep="\t", columns=songplay_columns)


def process_data(cur, conn, filepath, func):
    """
    Description: This function is responsible for traversing through the directories and pass
    the data filepath to the transformation functions

    Arguments:
        cur: Cursor object.
        conn: Connection to the database.
        filepath: Log or song data file path.
        func: function that further process the song or log data to transform and persist into database

    Returns:
        None
    """
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root, "*.json"))
        for f in files:
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print("{} files found in {}".format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print("{}/{} files processed.".format(i, num_files))


def main():
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath="data/song_data", func=process_song_file)
    process_data(cur, conn, filepath="data/log_data", func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()
