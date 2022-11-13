package publisher

import (
	"context"
	"log"
)

type virtualPublisher struct {
}

func (g virtualPublisher) Publish(ctx context.Context, topicName string, data interface{}) error {
	log.Printf("Publishing %T to %s", data, topicName)
	return nil
}
