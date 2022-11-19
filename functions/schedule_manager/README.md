# Schedule manager

Fetch the schedule for the entire year and save it to the store, if it has changed since last fetch.

Invoke by sending a pubsub message to topic "topic_update_schedule" that looks like this:

```
{
    "year": 2022,
}
```

year is optional, and will default to today year if not supplied. In production we will not supply this value, it's used for testing.

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
        "data": "e30=",
    },
    "subscription": "projects/yards-dev/subscriptions/dev"
}
```

Where data is a base64 encoded string of valid JSON, as described above.
