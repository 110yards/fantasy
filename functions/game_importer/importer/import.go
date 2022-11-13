package importer

import (
	"context"
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/mdryden/110yards/functions/gameimporter/publisher"
	"github.com/mdryden/110yards/functions/gameimporter/store"
)

func ImportGames(key string, year int, currentDate time.Time, daysBack, daysForward int) error {
	log.Printf("Importing %d games using date %v", year, currentDate)

	allGames, err := GetGamesForSeason(key, year)

	if err != nil {
		return fmt.Errorf("failed to fetch games for %d: %v", year, err)
	}

	recent, err := FilterRecentGames(allGames, currentDate, daysBack, daysForward)
	if err != nil {
		return fmt.Errorf("Failed to filter recent games %v", err)
	}

	log.Printf("Found %d recent games", len(recent))

	changed, err := getChangedGames(key, year, recent)
	if err != nil {
		return fmt.Errorf("Failed to get changed games %v", err)
	}

	log.Printf("Found %d updated games", len(changed))

	for _, g := range changed {
		if err := PublishGame(g); err != nil {
			return fmt.Errorf("Failed to publish game %d/%d: %v", year, g.GameId, err)
		}
		log.Printf("Published %d/%d", year, g.GameId)

		if err := SaveGameHash(year, g); err != nil {
			return fmt.Errorf("Failed to save game hash %d/%d: %v", year, g.GameId, err)
		}
		log.Printf("Saved hash for %d/%d", year, g.GameId)
	}

	return nil
}

func getChangedGames(key string, year int, recentGames JsonArray) ([]ChangedGame, error) {

	changed := make([]ChangedGame, 0)
	timestamp := time.Now()

	for _, g := range recentGames {
		v, exists := g["game_id"]
		if !exists {
			return nil, errors.New("game_id not found in game data")
		}

		f, ok := v.(float64)
		if !ok {
			return nil, fmt.Errorf("expected game_id to be an float, but it was: %T\n", v)
		}

		gameId := int(f)
		log.Printf("Fetching game %d/%d", year, gameId)
		game, err := GetFullGame(key, year, gameId)

		if err != nil {
			return nil, err
		}

		hash, err := CalculateHash(game)

		if err != nil {
			return nil, err
		}

		previousHash, err := ReadGameHash(year, gameId)

		if err != nil {
			return nil, err
		}

		if previousHash == hash {
			continue
		}

		cg := ChangedGame{
			GameId:    gameId,
			Hash:      hash,
			Timestamp: timestamp,
			Data:      game,
		}

		changed = append(changed, cg)

	}

	return changed, nil
}

func getGamePath(year, gameId int) string {
	return fmt.Sprintf("game_importer/games/%d/game/%d", year, gameId)
}

func ReadGameHash(year int, gameId int) (string, error) {
	gamePath := getGamePath(year, gameId)
	hashPath := fmt.Sprintf("%s/hash", gamePath)

	var hash string
	err := store.ReadPath(context.Background(), hashPath, &hash)

	if err != nil {
		return "", err
	}

	return hash, nil
}

func PublishGame(game ChangedGame) error {
	return publisher.Instance.Publish(context.Background(), "topic_game_updated", game.Data)
}

func SaveGameHash(year int, game ChangedGame) error {
	path := getGamePath(year, game.GameId)
	return store.SetPath(context.Background(), path, game)
}
