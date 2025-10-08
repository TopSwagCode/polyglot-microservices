package task

import "time"

const (
	StatusOpen       = "open"
	StatusInProgress = "in_progress"
	StatusCompleted  = "completed"
	StatusClosed     = "closed"
)

const (
	PriorityLow      = "low"
	PriorityMedium   = "medium"
	PriorityHigh     = "high"
	PriorityCritical = "critical"
)

type Task struct {
	ID          uint      `gorm:"primaryKey"`
	Title       string    `gorm:"not null"`
	Description string
	ProjectID   uint      `gorm:"not null;index"`
	Status      string    `gorm:"default:'open'"`
	Priority    string    `gorm:"default:'medium'"`
	UserID      string    `gorm:"not null;index"`
	Username    string    `gorm:"not null"`
	CreatedAt   time.Time
	UpdatedAt   time.Time
}
