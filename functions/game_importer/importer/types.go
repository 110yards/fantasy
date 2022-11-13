package importer

import (
	"time"
)

type JsonObject map[string]interface{}

type JsonArray []JsonObject

type ResponseType interface {
	JsonObject | JsonArray
}

type ChangedGame struct {
	GameId    int        `json:"game_id"`
	Hash      string     `json:"hash"`
	Timestamp time.Time  `json:"timestamp"`
	Data      JsonObject `json:"-"`
}
