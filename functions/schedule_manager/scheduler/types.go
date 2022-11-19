package scheduler

import "time"

type GamesResponse struct {
	Games []Game `json:"data"`
}

type Schedule struct {
	Season int          `json:"season"`
	Games  map[int]Game `json:"games"`
	Hash   string       `json:"hash"`
}

type Game struct {
	GameId     int       `json:"game_id"`
	DateStart  time.Time `json:"date_start"`
	GameNumber int       `json:"game_number"`
	Week       int       `json:"week"`
	Season     int       `json:"season"`
	EventType  EventType `json:"event_type"`
	Team1      Team      `json:"team_1"`
	Team2      Team      `json:"team_2"`
}

type EventType struct {
	EventTypeId int    `json:"event_type_id"`
	Name        string `json:"name"`
	Title       string `json:"title"`
}

type Team struct {
	TeamId       int    `json:"team_id"`
	Location     string `json:"location"`
	Nickname     string `json:"nickname"`
	Abbreviation string `json:"abbreviation"`
}
