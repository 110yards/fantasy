package gameimporter

import (
	"context"
	"encoding/json"
	"log"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/mdryden/110yards/functions/scoreboardupdater/environment"
	"github.com/mdryden/110yards/functions/scoreboardupdater/store"
	"github.com/mdryden/110yards/functions/scoreboardupdater/updater"
)

func init() {
	environment.Setup()
	store.Initialize(environment.RtdbEmulatorHost, environment.ProjectId)

	functions.CloudEvent("scoreboard-updater", updateScoreboardHandler)
}

type EventPayload struct {
	Message struct {
		Data []byte `json:"data"`
	}
}

func updateScoreboardHandler(ctx context.Context, e event.Event) error {
	var msg EventPayload
	if err := e.DataAs(&msg); err != nil {
		log.Printf("event.DataAs: %v", err)
		return nil // always ack
	}

	var data updater.Game
	err := json.Unmarshal(msg.Message.Data, &data)

	if err != nil {
		log.Printf("failed to unmarshal data: %v", err)
		return nil // always ack
	}

	err = updater.UpdateScoreboard(data)

	if err != nil {
		log.Printf("failed to update scoreboard: %v", err)
		return nil // always ack
	}

	return nil
}
