package models

import (
	"time"
)

// Project represents a project that can contain multiple tasks
type Project struct {
	ID        uint      `json:"id" gorm:"primaryKey"`
	Name      string    `json:"name" gorm:"not null"`
	UserID    string    `json:"user_id" gorm:"not null;index"`
	Username  string    `json:"username" gorm:"not null"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
	
	// Associations
	Tasks []Task `json:"tasks,omitempty" gorm:"foreignKey:ProjectID"`
}

// CreateProjectRequest represents the request body for creating a project
type CreateProjectRequest struct {
	Name string `json:"name" validate:"required,min=1,max=100"`
}

// UpdateProjectRequest represents the request body for updating a project
type UpdateProjectRequest struct {
	Name string `json:"name" validate:"required,min=1,max=100"`
}