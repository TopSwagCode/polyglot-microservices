package project

import (
	"context"
	"fmt"

	"gorm.io/gorm"
)

type GormRepository struct { db *gorm.DB }

func NewGormRepository(db *gorm.DB) *GormRepository { return &GormRepository{db: db} }

func (r *GormRepository) Create(ctx context.Context, p *Project) error {
	return r.db.WithContext(ctx).Create(p).Error
}

func (r *GormRepository) GetByID(ctx context.Context, id uint, userID string) (*Project, error) {
	var p Project
	err := r.db.WithContext(ctx).Where("id = ? AND user_id = ?", id, userID).First(&p).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound { return nil, ErrNotFound }
		return nil, fmt.Errorf("get project: %w", err)
	}
	return &p, nil
}

func (r *GormRepository) ListByUser(ctx context.Context, userID string) ([]Project, error) {
	var ps []Project
	if err := r.db.WithContext(ctx).Where("user_id = ?", userID).Find(&ps).Error; err != nil {
		return nil, fmt.Errorf("list projects: %w", err)
	}
	return ps, nil
}
