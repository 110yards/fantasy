# Games Importer

Fetches games within a window of days, usually today - X and today + Y.

Invoke by sending a pubsub message to topic "topic_import_games" that looks like this:

```
{
    "year": 2022,
    "simulationDate": "2022-06-09T21:00:00-04:00",
    "daysBack": 2,
    "daysForward": 1
}
```

year and simulationDate are optional, and will default to today's date and year.

## Running in dev

You will need a .env file:

```
IS_DEV=true
CFL_API_KEY=<key>
GCLOUD_PROJECT=yards-dev
RTDB_EMULATOR_HOST="localhost:9001"
```

And the firebase emulators should be running.

To start the function, navigate to the function directory and run the following command:

```
$ ./run.sh
```

Then use a REST client or something to post the following payload to `localhost:8080/projects/yards-dev/topics/topic_import_games`:

```
{
    "message": {
        "data": "ewogICAgICAgICAgICAieWVhciI6IDIwMjIsCiAgICAgICAgICAgICJzaW11bGF0aW9uRGF0ZSI6ICIyMDIyLTA2LTA5VDIxOjAwOjAwLTA0OjAwIiwKICAgICAgICAgICAgImRheXNCYWNrIjogMiwKICAgICAgICAgICAgImRheXNGb3J3YXJkIjogMQogICAgICAgIH0=",
    },
    "subscription": "projects/yards-dev/subscriptions/dev"
}
```

Where data is a base64 encoded string of valid JSON, as described above.
