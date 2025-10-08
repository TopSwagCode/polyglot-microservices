package task

import (
	"context"
	"fmt"

	"gorm.io/gorm"
)

type GormRepository struct { db *gorm.DB }

func NewGormRepository(db *gorm.DB) *GormRepository { return &GormRepository{db: db} }

func (r *GormRepository) Create(ctx context.Context, t *Task) error {
	return r.db.WithContext(ctx).Create(t).Error
}

func (r *GormRepository) GetByID(ctx context.Context, id uint, userID string) (*Task, error) {
	var t Task
	err := r.db.WithContext(ctx).Where("id = ? AND user_id = ?", id, userID).First(&t).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound { return nil, ErrNotFound }
		return nil, fmt.Errorf("get task: %w", err)
	}
	return &t, nil
}

func (r *GormRepository) ListByUser(ctx context.Context, userID string) ([]Task, error) {
	var ts []Task
	if err := r.db.WithContext(ctx).Where("user_id = ?", userID).Find(&ts).Error; err != nil {
		return nil, fmt.Errorf("list tasks: %w", err)
	}
	return ts, nil
}

func (r *GormRepository) ListByProject(ctx context.Context, projectID uint, userID string) ([]Task, error) {
	var ts []Task
	if err := r.db.WithContext(ctx).Where("project_id = ? AND user_id = ?", projectID, userID).Find(&ts).Error; err != nil {
		return nil, fmt.Errorf("list tasks by project: %w", err)
	}
	return ts, nil
}

func (r *GormRepository) Update(ctx context.Context, t *Task) error {
	return r.db.WithContext(ctx).Save(t).Error
}
