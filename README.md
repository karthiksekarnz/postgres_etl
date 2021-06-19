## Udacity Data Engineering Nanodegree - PostGres ETL project
This project's objective is to create a star schema for songplay analysis.

### Fact Table
- songplays - records in log data associated with song plays i.e. records with page NextSong

### Dimension Tables
- users - users in the app
- songs - songs in music database
- artists - artists in music database
- time - timestamps of records in songplays broken down into specific units

### Something Extra
I've used copy command to bulk insert log data into the database instead of multiple insert queries.<br>
You can find the copy command below in ``etl.py`` under ``process_log_file`` function.
```
cur.copy_from(str_buffer, "songplays", sep="\t", columns=songplay_columns)
```
### Prerequesites
This project requires ``pandas`` and ``psycopg2`` packages installed.<br>
You can install them using pip command like ``pip3 install psycopg2``

### Instructions to run the project
- Run ``python3 ./create_tables.py`` command to drop already existing tables and create the tables.
- Then run ``python3 ./etl.py`` command to run the etl script to process the song and log data and import them into the database.

### Schema diagram
Following is the database schema diagram.
![Screen Shot 2021-06-20 at 11 36 55 AM](https://user-images.githubusercontent.com/2171885/122658024-b8d5ac80-d1bc-11eb-8ee0-ad9b5303b5df.png)
