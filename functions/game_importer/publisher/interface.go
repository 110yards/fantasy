package publisher

import "context"

type Publisher interface {
	Publish(ctx context.Context, topicName string, data interface{}) error
}
