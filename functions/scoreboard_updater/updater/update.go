package updater

import (
	"context"
	"fmt"
	"log"

	"github.com/mdryden/110yards/functions/scoreboardupdater/store"
)

func UpdateScoreboard(game Game) error {
	hash, err := CalculateHash(game)
	if err != nil {
		return err
	}

	previousHash, err := ReadGameHash(game.Season, game.Week, game.GameId)
	if err != nil {
		return err
	}

	if hash == previousHash {
		log.Print("Game has not changed")
		return nil
	}

	game.Hash = hash

	err = SaveGame(game)

	if err != nil {
		return fmt.Errorf("Failed to save game: %v", err)
	}

	log.Printf("Updated game %d/%d", game.Season, game.GameId)
	return nil
}

func getGamePath(year, week, gameId int) string {
	return fmt.Sprintf("scoreboard/season/%d/week/%d/game/%d", year, week, gameId)
}

func ReadGameHash(year, week, gameId int) (string, error) {
	gamePath := getGamePath(year, week, gameId)
	hashPath := fmt.Sprintf("%s/hash", gamePath)

	var hash string
	err := store.ReadPath(context.Background(), hashPath, &hash)

	if err != nil {
		return "", err
	}

	return hash, nil
}

func SaveGame(game Game) error {
	path := getGamePath(game.Season, game.Week, game.GameId)
	return store.SetPath(context.Background(), path, game)
}
