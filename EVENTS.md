# Event Architecture

110 Yards is an event-driven system, and in 2023 many of those events have been refactored to be isolated from the rest of the system.

Here is a high level overview of how the event system works:

## Schedule Manager

Once per day, the schedule-manager function fetches this year's games from the CFL and reshapes it into a schedule arranged by segment (preseason, regular, playoffs) and determines where in the schedule we are (which segment, which week).

If the state or schedule has changed, it's saved to firebase.

To be considered: This could be further subdivided into the manager (which fetches games and reshapes into a schedule object), and a Schedule State Manager (or something) which fetches the current schedule from firebase and update the current week (if it's changed).

## Game Importer

On a short interval (currently 5 minutes), the game importer fetches the current week # from the schedule state, and the games from the current week are fetched from the CFL.

Games are hashed, and then the previous hash (if it exists) for that game is fetched from firebase.

If any game hash has changed, the game data is published to "topic_game_updated".

## Scoreboard Updater

Listens to "topic_game_updated" and creates a scoreboard object as games changes. Games are reduced to a smaller map in order to ensure we are only updating parts of the game which affect the scoreboard (ie: not player stats).

## Player Locks (future)

Listens to "topic_game_updated" and creates a lock object for teams involved in an active game. Only writes if the state of the lock has changed.

Locks should be stored by week, so they become obsolete when the schedule state updates.

## Player Stats Updater

Listens to "topic_game_updated" and pulls out the player stats for each player in the game. Compares the player stats hash to the hash we currently have in firebase, and updates each player which has changed.

## Season Stats Calculator

TBD
