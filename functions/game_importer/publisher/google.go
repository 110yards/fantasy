package publisher

import (
	"context"
	"encoding/json"

	"cloud.google.com/go/pubsub"
)

type googlePublisher struct {
	projectId string
}

func (g googlePublisher) Publish(ctx context.Context, topicName string, data interface{}) error {
	client, err := pubsub.NewClient(ctx, g.projectId)

	if err != nil {
		return err
	}
	defer client.Close()

	t := client.Topic(topicName)

	payload, err := json.Marshal(data)

	if err != nil {
		return err
	}

	result := t.Publish(ctx, &pubsub.Message{
		Data: payload,
	})

	_, err = result.Get(ctx)
	return err
}