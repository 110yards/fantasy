package gameimporter

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/mdryden/110yards/functions/gameimporter/environment"
	"github.com/mdryden/110yards/functions/gameimporter/importer"
	"github.com/mdryden/110yards/functions/gameimporter/publisher"
	"github.com/mdryden/110yards/functions/gameimporter/store"
)

func init() {
	environment.Setup()
	store.Initialize(environment.RtdbEmulatorHost, environment.ProjectId)
	publisher.Initialize(environment.IsDev, environment.ProjectId)

	functions.CloudEvent("game-importer", importGamesHandler)
}

type EventPayload struct {
	Message struct {
		Data []byte `json:"data"`
	}
}

func importGamesHandler(ctx context.Context, e event.Event) error {
	var msg EventPayload
	if err := e.DataAs(&msg); err != nil {
		log.Printf("event.DataAs: %v", err)
		return nil // always ack
	}

	type importMessage struct {
		Year           int       `json:"year"`
		SimulationDate time.Time `json:"simulationDate"`
		DaysBack       int       `json:"daysBack"`
		DaysForward    int       `json:"daysForward"`
	}

	var data importMessage
	err := json.Unmarshal(msg.Message.Data, &data)

	if err != nil {
		log.Printf("failed to unmarshal data: %v", err)
		return nil // always ack
	}

	year := data.Year
	if year == 0 {
		year = time.Now().Year()
	}

	currentDate := data.SimulationDate
	if currentDate.IsZero() {
		currentDate = time.Now()
	}

	daysBack := data.DaysBack
	daysForward := data.DaysForward

	err = importer.ImportGames(environment.CflKey, year, currentDate, daysBack, daysForward)

	if err != nil {
		log.Printf("failed to import games: %v", err)
		return nil // always ack
	}

	return nil
}
