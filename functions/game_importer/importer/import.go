package importer

import (
	"errors"
	"fmt"
	"log"
	"time"
)

func ImportGames(key string, year int, currentDate time.Time, daysBack, daysForward int) error {
	log.Printf("Importing %d games using date %v", year, currentDate)

	allGames, err := GetGamesForSeason(key, year)

	if err != nil {
		return fmt.Errorf("failed to fetch games for %d: %v", year, err)
	}

	recent, err := FilterRecentGames(allGames, currentDate, daysBack, daysForward)

	log.Printf("Found %d recent games", len(recent))

	for _, g := range recent {
		v, exists := g["game_id"]
		if !exists {
			return errors.New("game_id not found in game data")
		}

		gameId, ok := v.(int)
		if !ok {
			return errors.New("game_id is not an int")
		}

		log.Printf("Fetching game %d/%d", year, gameId)
		_, err := GetFullGame(key, year, gameId)

		if err != nil {
			return err
		}
	}

	return nil
}
