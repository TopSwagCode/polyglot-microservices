package db

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/domain/task"
	"gorm.io/gorm"
)

type TaskRepository struct { db *gorm.DB }

func NewTaskRepository(db *gorm.DB) *TaskRepository { return &TaskRepository{db: db} }

func (r *TaskRepository) Create(ctx context.Context, t *task.Task) error { return r.db.WithContext(ctx).Create(t).Error }

func (r *TaskRepository) GetByID(ctx context.Context, id uint, userID string) (*task.Task, error) {
	var t task.Task
	err := r.db.WithContext(ctx).Where("id = ? AND user_id = ?", id, userID).First(&t).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound { return nil, fmt.Errorf("not found") }
		return nil, fmt.Errorf("get task: %w", err)
	}
	return &t, nil
}

func (r *TaskRepository) ListByUser(ctx context.Context, userID string) ([]task.Task, error) {
	var ts []task.Task
	if err := r.db.WithContext(ctx).Where("user_id = ?", userID).Find(&ts).Error; err != nil { return nil, fmt.Errorf("list tasks: %w", err) }
	return ts, nil
}

func (r *TaskRepository) ListByProject(ctx context.Context, projectID uint, userID string) ([]task.Task, error) {
	var ts []task.Task
	if err := r.db.WithContext(ctx).Where("project_id = ? AND user_id = ?", projectID, userID).Find(&ts).Error; err != nil { return nil, fmt.Errorf("list tasks by project: %w", err) }
	return ts, nil
}

func (r *TaskRepository) Update(ctx context.Context, t *task.Task) error { return r.db.WithContext(ctx).Save(t).Error }
