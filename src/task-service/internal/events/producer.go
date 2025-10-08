package events

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/IBM/sarama"
)

// Producer handles Kafka event publishing
type Producer struct {
	producer sarama.SyncProducer
	topic    string
}

// TaskEvent represents a task-related event
type TaskEvent struct {
	Event     string    `json:"event"`
	TaskID    uint      `json:"task_id"`
	ProjectID uint      `json:"project_id"`
	Title     string    `json:"title"`
	Status    string    `json:"status"`
	UserID    string    `json:"user_id"`
	Username  string    `json:"username"`
	Timestamp time.Time `json:"timestamp"`
}

// ProjectEvent represents a project-related event
type ProjectEvent struct {
	Event     string    `json:"event"`
	ProjectID uint      `json:"project_id"`
	Name      string    `json:"name"`
	UserID    string    `json:"user_id"`
	Username  string    `json:"username"`
	Timestamp time.Time `json:"timestamp"`
}

// NewProducer creates a new Kafka producer
func NewProducer() (*Producer, error) {
	brokerURL := os.Getenv("KAFKA_BROKER")
	if brokerURL == "" {
		brokerURL = "kafka:9092"
	}

	topic := os.Getenv("KAFKA_TOPIC")
	if topic == "" {
		topic = "task-events"
	}

	slog.Info("Creating Kafka producer", "broker", brokerURL, "topic", topic)

	config := sarama.NewConfig()
	config.Producer.RequiredAcks = sarama.WaitForAll
	config.Producer.Retry.Max = 5
	config.Producer.Return.Successes = true
	config.Producer.Partitioner = sarama.NewRandomPartitioner

	producer, err := sarama.NewSyncProducer([]string{brokerURL}, config)
	if err != nil {
		return nil, fmt.Errorf("failed to create Kafka producer: %w", err)
	}

	slog.Info("Kafka producer created successfully")

	return &Producer{
		producer: producer,
		topic:    topic,
	}, nil
}

// PublishTaskEvent publishes a task-related event
func (p *Producer) PublishTaskEvent(eventType string, taskID, projectID uint, title, status, userID, username string) error {
	event := TaskEvent{
		Event:     eventType,
		TaskID:    taskID,
		ProjectID: projectID,
		Title:     title,
		Status:    status,
		UserID:    userID,
		Username:  username,
		Timestamp: time.Now(),
	}

	return p.publishEvent(event)
}

// PublishProjectEvent publishes a project-related event
func (p *Producer) PublishProjectEvent(eventType string, projectID uint, name, userID, username string) error {
	event := ProjectEvent{
		Event:     eventType,
		ProjectID: projectID,
		Name:      name,
		UserID:    userID,
		Username:  username,
		Timestamp: time.Now(),
	}

	return p.publishEvent(event)
}

// publishEvent publishes an event to Kafka
func (p *Producer) publishEvent(event interface{}) error {
	eventBytes, err := json.Marshal(event)
	if err != nil {
		return fmt.Errorf("failed to marshal event: %w", err)
	}

	message := &sarama.ProducerMessage{
		Topic: p.topic,
		Value: sarama.StringEncoder(eventBytes),
	}

	partition, offset, err := p.producer.SendMessage(message)
	if err != nil {
		slog.Error("Failed to publish event", "error", err, "event", string(eventBytes))
		return fmt.Errorf("failed to publish event: %w", err)
	}

	slog.Info("Event published successfully", "partition", partition, "offset", offset, "event", string(eventBytes))
	return nil
}

// Close closes the Kafka producer
func (p *Producer) Close() error {
	if p.producer != nil {
		return p.producer.Close()
	}
	return nil
}

// Event type constants
const (
	EventTaskCreated   = "task_created"
	EventTaskUpdated   = "task_updated"
	EventTaskDeleted   = "task_deleted"
	EventProjectCreated = "project_created"
	EventProjectUpdated = "project_updated"
	EventProjectDeleted = "project_deleted"
)