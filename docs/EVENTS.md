# System and League Events

## System Events

### End of Day

The End of Day event triggers other workflows. Currently there are logic paths:

1. "Should start waivers" - occurs when the last game of the week has been completed long enough to calculate results, and waivers are not already active. This triggers the "End of Week" event

2. "Should process waivers" - occurs on the next run after waivers have been started (24 hrs later). This triggers the "League Process Waivers" event.

### End of Week

The End of Week event performs some system tasks, then triggers other tasks:

1. Recalculate season stats - updates stats for all players with stats for the week which just ended.

2. Trigger League End of Week event

## League Events

### League Process Waivers

Process waiver claims for a single league. This event is triggered by System / End of Day, and runs asynchronously for all subscribed leagues.

### League End of Week

1. Calculate and save weekly score and update season score for players who played in the week which just ended. Rank all players
   based on league scoring settings.

2. Calculate matchup results and update league standings.

3. If upcoming week is a playoff week, calculate playoff matchups.
