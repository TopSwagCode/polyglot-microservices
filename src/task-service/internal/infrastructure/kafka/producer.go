package kafka

import (
	"context"
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/IBM/sarama"
)

type Producer interface {
	ProjectCreated(ctx context.Context, projectID uint, name, userID, username string) error
	TaskCreated(ctx context.Context, taskID, projectID uint, title, status, userID, username string) error
	TaskUpdated(ctx context.Context, taskID, projectID uint, title, status, userID, username string) error
}

type KafkaProducer struct {
	producer     sarama.SyncProducer
	taskTopic    string
	projectTopic string
}

func NewKafkaProducer() (*KafkaProducer, error) {
	broker := getenv("KAFKA_BROKER", "kafka:9092")
	taskTopic := getenv("KAFKA_TOPIC", "task-events")
	projectTopic := getenv("KAFKA_PROJECT_TOPIC", "project-events")
	cfg := sarama.NewConfig()
	cfg.Producer.RequiredAcks = sarama.WaitForAll
	cfg.Producer.Retry.Max = 5
	cfg.Producer.Return.Successes = true
	p, err := sarama.NewSyncProducer([]string{broker}, cfg)
	if err != nil { return nil, fmt.Errorf("create kafka producer: %w", err) }
	slog.Info("kafka producer ready", "broker", broker, "taskTopic", taskTopic, "projectTopic", projectTopic)
	return &KafkaProducer{producer: p, taskTopic: taskTopic, projectTopic: projectTopic}, nil
}

func (k *KafkaProducer) publish(topic string, event string, payload any) error {
	b, err := json.Marshal(map[string]any{
		"event": event,
		"timestamp": time.Now().UTC().Format(time.RFC3339Nano),
		"data": payload,
	})
	if err != nil { return fmt.Errorf("marshal: %w", err) }
	msg := &sarama.ProducerMessage{Topic: topic, Value: sarama.ByteEncoder(b)}
	partition, offset, err := k.producer.SendMessage(msg)
	if err != nil { return fmt.Errorf("send message: %w", err) }
	slog.Info("event published", "event", event, "topic", topic, "partition", partition, "offset", offset)
	return nil
}

func (k *KafkaProducer) ProjectCreated(ctx context.Context, projectID uint, name, userID, username string) error {
	return k.publish(k.projectTopic, "project.created", map[string]any{"id": projectID, "name": name, "user_id": userID, "username": username})
}
func (k *KafkaProducer) TaskCreated(ctx context.Context, taskID, projectID uint, title, status, userID, username string) error {
	return k.publish(k.taskTopic, "task.created", map[string]any{"id": taskID, "project_id": projectID, "title": title, "status": status, "user_id": userID, "username": username})
}
func (k *KafkaProducer) TaskUpdated(ctx context.Context, taskID, projectID uint, title, status, userID, username string) error {
	return k.publish(k.taskTopic, "task.updated", map[string]any{"id": taskID, "project_id": projectID, "title": title, "status": status, "user_id": userID, "username": username})
}

func (k *KafkaProducer) Close() error { if k.producer != nil { return k.producer.Close() }; return nil }

func getenv(k, d string) string { v := os.Getenv(k); if v == "" { return d }; return v }
