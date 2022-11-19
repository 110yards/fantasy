package schedulemanager

import (
	"context"
	"encoding/json"
	"log"
	"time"

	"github.com/GoogleCloudPlatform/functions-framework-go/functions"
	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/mdryden/110yards/functions/schedulemanager/environment"
	"github.com/mdryden/110yards/functions/schedulemanager/scheduler"
	"github.com/mdryden/110yards/functions/schedulemanager/store"
)

func init() {
	environment.Setup()
	store.Initialize(environment.RtdbEmulatorHost, environment.ProjectId)

	functions.CloudEvent("schedule-manager", manageScheduleHandler)
}

type EventPayload struct {
	Message struct {
		Data []byte `json:"data"`
	}
}

func manageScheduleHandler(ctx context.Context, e event.Event) error {
	var msg EventPayload
	if err := e.DataAs(&msg); err != nil {
		log.Printf("event.DataAs: %v", err)
		return nil // always ack
	}

	type message struct {
		Year int `json:"year"`
	}

	var data message
	err := json.Unmarshal(msg.Message.Data, &data)

	if err != nil {
		log.Printf("failed to unmarshal data: %v", err)
		return nil // always ack
	}

	year := data.Year
	if year == 0 {
		year = time.Now().Year()
	}
	err = scheduler.UpdateSchedule(environment.CflKey, year)

	if err != nil {
		log.Printf("failed to import games: %v", err)
		return nil // always ack
	}

	return nil
}
