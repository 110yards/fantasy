package importer

import (
	"errors"
	"log"
	"time"
)

func FilterRecentGames(games JsonArray, currentDate time.Time, daysBack, daysForward int) (JsonArray, error) {
	recentGames := make(JsonArray, 0)

	if daysBack > 0 {
		daysBack *= -1
	}

	ignoreBefore := currentDate.AddDate(0, 0, daysBack)
	ignoreAfter := currentDate.AddDate(0, 0, daysForward)

	log.Printf("Ignoring games before %v and after  %v", ignoreBefore, ignoreAfter)

	for _, g := range games {
		v, exists := g["date_start"]
		if !exists {
			return nil, errors.New("date_start field missing from game data")
		}

		start, err := ParseIsoString(v.(string))

		if err != nil {
			return nil, err
		}

		if start.After(ignoreBefore) && start.Before(ignoreAfter) {
			recentGames = append(recentGames, g)
		}
	}

	return recentGames, nil
}

// func FindChangedGames(games []Game) ([]Game, error) {
// }
