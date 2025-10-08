package project

import "context"

// Repository defines persistence operations for Projects.
type Repository interface {
	Create(ctx context.Context, p *Project) error
	GetByID(ctx context.Context, id uint, userID string) (*Project, error)
	ListByUser(ctx context.Context, userID string) ([]Project, error)
}
