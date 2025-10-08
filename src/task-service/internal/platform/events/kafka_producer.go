package events

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/IBM/sarama"
)

// KafkaProducer implements Publisher using Apache Kafka.
type KafkaProducer struct {
	producer      sarama.SyncProducer
	defaultTopic  string // task events topic
	projectTopic  string // project events topic (optional)
}

// NewKafkaProducer creates a new Kafka producer.
func NewKafkaProducer() (*KafkaProducer, error) {
	brokerURL := os.Getenv("KAFKA_BROKER")
	if brokerURL == "" { brokerURL = "kafka:9092" }

	topic := os.Getenv("KAFKA_TOPIC")
	if topic == "" { topic = "task-events" }
	projectTopic := os.Getenv("KAFKA_PROJECT_TOPIC")
	if projectTopic == "" { projectTopic = "project-events" }

	cfg := sarama.NewConfig()
	cfg.Producer.RequiredAcks = sarama.WaitForAll
	cfg.Producer.Retry.Max = 5
	cfg.Producer.Return.Successes = true
	cfg.Producer.Partitioner = sarama.NewRandomPartitioner

	p, err := sarama.NewSyncProducer([]string{brokerURL}, cfg)
	if err != nil {
		return nil, fmt.Errorf("create kafka producer: %w", err)
	}

	slog.Info("Kafka producer initialized", "broker", brokerURL, "taskTopic", topic, "projectTopic", projectTopic)
	return &KafkaProducer{producer: p, defaultTopic: topic, projectTopic: projectTopic}, nil
}

// Publish publishes an event to Kafka.
func (k *KafkaProducer) Publish(ctx context.Context, evt Event) error {
	if k == nil || k.producer == nil { return nil }
	payload := map[string]interface{}{
		"event": evt.Name(),
		"key": evt.Key(),
		"timestamp": time.Now().UTC().Format(time.RFC3339Nano),
		"data": evt.Payload(),
	}
	b, err := json.Marshal(payload)
	if err != nil {
		return fmt.Errorf("marshal event: %w", err)
	}
	// Determine topic based on event name (simple prefix strategy)
	topic := k.defaultTopic
	if evtName := evt.Name(); len(evtName) >= 8 && evtName[:8] == "project." {
		if k.projectTopic != "" { topic = k.projectTopic }
	}
	msg := &sarama.ProducerMessage{Topic: topic, Value: sarama.ByteEncoder(b)}
	partition, offset, err := k.producer.SendMessage(msg)
	if err != nil { return fmt.Errorf("send kafka message: %w", err) }
	slog.Info("event published", "event", evt.Name(), "topic", topic, "partition", partition, "offset", offset)
	return nil
}

// Close closes the underlying producer.
func (k *KafkaProducer) Close() error {
	if k != nil && k.producer != nil { return k.producer.Close() }
	return nil
}
