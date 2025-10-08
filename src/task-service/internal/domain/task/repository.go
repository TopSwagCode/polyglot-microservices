package task

import "context"

type Repository interface {
	Create(ctx context.Context, t *Task) error
	GetByID(ctx context.Context, id uint, userID string) (*Task, error)
	ListByUser(ctx context.Context, userID string) ([]Task, error)
	ListByProject(ctx context.Context, projectID uint, userID string) ([]Task, error)
	Update(ctx context.Context, t *Task) error
}
