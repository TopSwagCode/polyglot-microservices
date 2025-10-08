package task

import "time"

// Status represents task lifecycle state.
const (
	StatusOpen       = "open"
	StatusInProgress = "in_progress"
	StatusCompleted  = "completed"
	StatusClosed     = "closed"
)

// Priority levels.
const (
	PriorityLow      = "low"
	PriorityMedium   = "medium"
	PriorityHigh     = "high"
	PriorityCritical = "critical"
)

// Task domain model.
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
