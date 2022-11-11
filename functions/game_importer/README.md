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
