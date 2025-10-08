package project

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/platform/events"
)

// Service provides project business logic.
type Service struct {
	repo      Repository
	publisher events.Publisher
}

func NewService(r Repository, p events.Publisher) *Service { return &Service{repo: r, publisher: p} }

// Create creates a new project.
func (s *Service) Create(ctx context.Context, name, userID, username string) (*Project, error) {
	if name == "" { return nil, fmt.Errorf("name required") }
	p := &Project{Name: name, UserID: userID, Username: username}
	if err := s.repo.Create(ctx, p); err != nil { return nil, err }
	if s.publisher != nil {
		_ = s.publisher.Publish(ctx, events.ProjectCreated{ID: p.ID, ProjectName: p.Name, UserID: userID, Username: username})
	}
	return p, nil
}

func (s *Service) Get(ctx context.Context, id uint, userID string) (*Project, error) {
	return s.repo.GetByID(ctx, id, userID)
}

func (s *Service) List(ctx context.Context, userID string) ([]Project, error) {
	return s.repo.ListByUser(ctx, userID)
}
