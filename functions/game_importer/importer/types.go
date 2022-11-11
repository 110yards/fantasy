package importer

type JsonObject map[string]interface{}

type JsonArray []JsonObject

type ResponseType interface {
	JsonObject | JsonArray
}

type HashStore interface {
	GetHash(gameId string) (string, error)
}
