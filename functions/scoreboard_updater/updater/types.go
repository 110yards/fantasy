package updater

import "time"

type EventType struct {
	EventTypeId int    `json:"event_type_id"`
	Name        string `json:"name"`
	Title       string `json:"title"`
}

type EventStatus struct {
	EventStatusId int    `json:"event_status_id"`
	Name          string `json:"name"`
	IsActive      bool   `json:"is_active"`
	Quarter       int    `json:"quarter"`
	Minutes       int    `json:"minutes"`
	Seconds       int    `json:"seconds"`
	Down          int    `json:"down"`
	YardsToGo     int    `json:"yards_to_go"`
}

type Linescore struct {
	Quarter int `json:"quarter"`
	Score   int `json:"score"`
}

type Team struct {
	TeamId       int         `json:"team_id"`
	Location     string      `json:"location"`
	Nickname     string      `json:"nickname"`
	Abbreviation string      `json:"abbreviation"`
	Score        int         `json:"score"`
	Linescores   []Linescore `json:"linescores"`
	IsAtHome     bool        `json:"is_at_home"`
	IsWinner     bool        `json:"is_winner"`
}

type Game struct {
	GameId      int         `json:"game_id"`
	DateStart   time.Time   `json:"date_start"`
	Week        int         `json:"week"`
	Season      int         `json:"season"`
	EventType   EventType   `json:"event_type"`
	EventStatus EventStatus `json:"event_status"`
	Team1       Team        `json:"team_1"`
	Team2       Team        `json:"team_2"`
	Hash        string      `json:"hash"`
}
