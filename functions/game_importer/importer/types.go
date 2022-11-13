package importer

import "time"

type JsonObject map[string]interface{}

type JsonArray []JsonObject

type ResponseType interface {
	JsonObject | JsonArray
}

type GameHash struct {
	GameId    int       `json:"gameId"`
	Hash      string    `json:"hash"`
	Timestamp time.Time `json:"lastUpdate"`
}

type ChangedGame struct {
	Data JsonObject
	Hash GameHash
}
