package publisher

import (
	"context"
	"fmt"
)

type googlePublisher struct {
}

func (g googlePublisher) Publish(ctx context.Context, topicName string, data interface{}) error {
	return fmt.Errorf("Not implemented")
}
