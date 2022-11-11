package importer

import (
	"fmt"
)

func GetGamesForSeason(key string, year int) (JsonArray, error) {
	path := fmt.Sprintf("games/%d?page[size]=100&filter[event_type_id][eq]=%d", year, eventTypeRegularSeason)

	games, err := getArray(key, path)

	if err != nil {
		return nil, err
	}

	return games, nil
}

func GetFullGame(key string, year, gameId int) (JsonObject, error) {
	path := fmt.Sprintf("games/%d/game/%d?include=boxscore,rosters,play_by_play", year, gameId)

	games, err := getArray(key, path)

	if err != nil {
		return nil, err
	}

	if len(games) != 1 {
		return nil, fmt.Errorf("failed to fetch game %d/%d", year, gameId)
	}

	return games[0], nil
}
