package events

import "context"

// Event is a domain event abstraction that can be published.
type Event interface {
	Name() string
	Key() string            // Partition/sharding key
	Payload() interface{}   // Serializable payload (JSON)
}

// Publisher publishes events to a backend (Kafka, NATS, etc.).
type Publisher interface {
	Publish(ctx context.Context, evt Event) error
	Close() error
}
