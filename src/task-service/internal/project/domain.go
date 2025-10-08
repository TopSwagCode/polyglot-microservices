package project

import "time"

// Project is the domain model for a project grouping tasks.
type Project struct {
	ID        uint      `gorm:"primaryKey"`
	Name      string    `gorm:"not null"`
	UserID    string    `gorm:"not null;index"`
	Username  string    `gorm:"not null"`
	CreatedAt time.Time
	UpdatedAt time.Time
}
