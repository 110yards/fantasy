# Event Architecture

110 Yards is an event-driven system, and in 2023 many of those events have been refactored to be isolated from the rest of the system.

Here is a high level overview of how the event system works:

## Schedule Manager

On a long interval (TBD, probably once per day), the schedule-manager function fetches this year's schedule from the CFL, checks for any changes to the properties we care about (mostly just week and date), and update the schedule if required.
