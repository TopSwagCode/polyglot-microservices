package db

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/domain/project"
	"gorm.io/gorm"
)

type ProjectRepository struct { db *gorm.DB }

func NewProjectRepository(db *gorm.DB) *ProjectRepository { return &ProjectRepository{db: db} }

func (r *ProjectRepository) Create(ctx context.Context, p *project.Project) error { return r.db.WithContext(ctx).Create(p).Error }

func (r *ProjectRepository) GetByID(ctx context.Context, id uint, userID string) (*project.Project, error) {
	var p project.Project
	err := r.db.WithContext(ctx).Where("id = ? AND user_id = ?", id, userID).First(&p).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound { return nil, fmt.Errorf("not found") }
		return nil, fmt.Errorf("get project: %w", err)
	}
	return &p, nil
}

func (r *ProjectRepository) ListByUser(ctx context.Context, userID string) ([]project.Project, error) {
	var ps []project.Project
	if err := r.db.WithContext(ctx).Where("user_id = ?", userID).Find(&ps).Error; err != nil { return nil, fmt.Errorf("list projects: %w", err) }
	return ps, nil
}
