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
		return err
	}

	log.Printf("Found %d recent games", len(recent))

	changed, err := getChangedGames(key, year, recent)
	if err != nil {
		return err
	}

	log.Printf("Found %d updated games", len(changed))

	for _, g := range changed {
		if err := PublishGame(g); err != nil {
			return err
		}
		log.Printf("Published %d/%d", year, g.Hash.GameId)

		SaveGameHash(year, g.Hash)
		log.Printf("Saved hash for %d/%d", year, g.Hash.GameId)
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

		if previousHash.Hash != hash {
			game["hash"] = hash
			game["timestamp"] = timestamp

			cg := ChangedGame{
				Data: game,
				Hash: GameHash{
					GameId:    gameId,
					Hash:      hash,
					Timestamp: timestamp,
				},
			}

			changed = append(changed, cg)
		}
	}

	return changed, nil
}

func getGameHashPath(year, gameId int) string {
	return fmt.Sprintf("game_importer/games/%d/game/%d", year, gameId)
}

func ReadGameHash(year int, gameId int) (*GameHash, error) {
	path := getGameHashPath(year, gameId)

	var gameHash GameHash
	err := store.ReadPath(context.Background(), path, &gameHash)

	if err != nil {
		return nil, err
	}

	return &gameHash, nil
}

func PublishGame(game ChangedGame) error {
	return publisher.Instance.Publish(context.Background(), "topic_game_updated", game.Data)
}

func SaveGameHash(year int, gameHash GameHash) error {
	path := getGameHashPath(year, gameHash.GameId)
	return store.SetPath(context.Background(), path, gameHash)
}
