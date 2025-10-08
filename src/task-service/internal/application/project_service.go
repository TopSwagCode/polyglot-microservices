package application

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/domain/project"
	"github.com/topswagcode/task-service/internal/infrastructure/kafka"
)

type ProjectService struct {
	repo      project.Repository
	producer  kafka.Producer
}

func NewProjectService(r project.Repository, p kafka.Producer) *ProjectService { return &ProjectService{repo: r, producer: p} }

func (s *ProjectService) Create(ctx context.Context, name, userID, username string) (*project.Project, error) {
	if name == "" { return nil, fmt.Errorf("name required") }
	p := &project.Project{Name: name, UserID: userID, Username: username}
	if err := s.repo.Create(ctx, p); err != nil { return nil, err }
	if s.producer != nil { _ = s.producer.ProjectCreated(ctx, p.ID, p.Name, userID, username) }
	return p, nil
}

func (s *ProjectService) Get(ctx context.Context, id uint, userID string) (*project.Project, error) {
	return s.repo.GetByID(ctx, id, userID)
}

func (s *ProjectService) List(ctx context.Context, userID string) ([]project.Project, error) {
	return s.repo.ListByUser(ctx, userID)
}
