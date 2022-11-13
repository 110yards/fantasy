package importer

type JsonObject map[string]interface{}

type JsonArray []JsonObject

type ResponseType interface {
	JsonObject | JsonArray
}

type ChangedGame struct {
	GameId int
	Data   JsonObject
}
