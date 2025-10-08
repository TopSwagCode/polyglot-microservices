package models

import (
	"time"
)

// Task represents a task within a project
type Task struct {
	ID          uint      `json:"id" gorm:"primaryKey"`
	Title       string    `json:"title" gorm:"not null"`
	Description string    `json:"description"`
	ProjectID   uint      `json:"project_id" gorm:"not null;index"`
	Status      string    `json:"status" gorm:"default:'open';check:status IN ('open', 'in_progress', 'completed', 'closed')"`
	Priority    string    `json:"priority" gorm:"default:'medium';check:priority IN ('low', 'medium', 'high', 'critical')"`
	UserID      string    `json:"user_id" gorm:"not null;index"`
	Username    string    `json:"username" gorm:"not null"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	
	// Associations
	Project Project `json:"project,omitempty" gorm:"foreignKey:ProjectID"`
}

// CreateTaskRequest represents the request body for creating a task
type CreateTaskRequest struct {
	Title       string `json:"title" validate:"required,min=1,max=200"`
	Description string `json:"description" validate:"max=1000"`
	ProjectID   uint   `json:"project_id" validate:"required"`
	Priority    string `json:"priority" validate:"omitempty,oneof=low medium high critical"`
}

// UpdateTaskRequest represents the request body for updating a task
type UpdateTaskRequest struct {
	Title       string `json:"title" validate:"omitempty,min=1,max=200"`
	Description string `json:"description" validate:"max=1000"`
	Status      string `json:"status" validate:"omitempty,oneof=open in_progress completed closed"`
	Priority    string `json:"priority" validate:"omitempty,oneof=low medium high critical"`
}

// TaskStatus constants
const (
	TaskStatusOpen       = "open"
	TaskStatusInProgress = "in_progress"
	TaskStatusCompleted  = "completed"
	TaskStatusClosed     = "closed"
)

// TaskPriority constants
const (
	TaskPriorityLow      = "low"
	TaskPriorityMedium   = "medium"
	TaskPriorityHigh     = "high"
	TaskPriorityCritical = "critical"
)