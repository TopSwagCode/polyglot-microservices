package task

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/platform/events"
)

// Service contains task business logic.
type Service struct {
	repo        Repository
	projectRepo ProjectAccessor // minimal interface to validate project ownership
	publisher   events.Publisher
}

// ProjectAccessor is a narrow interface used from project.Service to avoid cycle.
type ProjectAccessor interface { Get(ctx context.Context, id uint, userID string) (*ProjectRef, error) }

type ProjectRef struct { ID uint }

func NewService(r Repository, publisher events.Publisher, projectGetter ProjectAccessor) *Service {
	return &Service{repo: r, publisher: publisher, projectRepo: projectGetter}
}

// Create creates a new task.
func (s *Service) Create(ctx context.Context, title, desc string, projectID uint, priority, userID, username string) (*Task, error) {
	if title == "" { return nil, fmt.Errorf("title required") }
	if priority == "" { priority = PriorityMedium }
	// Validate project exists (best-effort)
	if s.projectRepo != nil {
		if _, err := s.projectRepo.Get(ctx, projectID, userID); err != nil {
			return nil, ErrProjectAccess
		}
	}
	t := &Task{Title: title, Description: desc, ProjectID: projectID, Status: StatusOpen, Priority: priority, UserID: userID, Username: username}
	if err := s.repo.Create(ctx, t); err != nil { return nil, err }
	if s.publisher != nil { _ = s.publisher.Publish(ctx, events.TaskCreated{ID: t.ID, ProjectID: t.ProjectID, Title: t.Title, Status: t.Status, UserID: userID, Username: username}) }
	return t, nil
}

func (s *Service) Get(ctx context.Context, id uint, userID string) (*Task, error) {
	return s.repo.GetByID(ctx, id, userID)
}

func (s *Service) List(ctx context.Context, userID string) ([]Task, error) { return s.repo.ListByUser(ctx, userID) }

func (s *Service) ListByProject(ctx context.Context, projectID uint, userID string) ([]Task, error) { return s.repo.ListByProject(ctx, projectID, userID) }

// Update modifies task fields.
func (s *Service) Update(ctx context.Context, id uint, title, desc, status, priority, userID, username string) (*Task, error) {
	t, err := s.repo.GetByID(ctx, id, userID)
	if err != nil { return nil, err }
	if title != "" { t.Title = title }
	if desc != "" { t.Description = desc }
	if status != "" { t.Status = status }
	if priority != "" { t.Priority = priority }
	if err := s.repo.Update(ctx, t); err != nil { return nil, err }
	if s.publisher != nil { _ = s.publisher.Publish(ctx, events.TaskUpdated{ID: t.ID, ProjectID: t.ProjectID, Title: t.Title, Status: t.Status, UserID: userID, Username: username}) }
	return t, nil
}
