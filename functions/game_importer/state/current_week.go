package state

import (
	"context"
	"fmt"

	"github.com/mdryden/110yards/functions/gameimporter/store"
)

type CurrentWeek struct {
	WeekNumber int    `json:"week_number"`
	WeekType   string `json:"week_type"`
	Games      []struct {
		GameId int `json:"game_id"`
	}
}

func GetCurrentWeek(year int) (CurrentWeek, error) {
	path := fmt.Sprintf("schedule/%d/current_week", year)

	var week CurrentWeek
	err := store.ReadPath(context.Background(), path, &week)

	return week, err
}
