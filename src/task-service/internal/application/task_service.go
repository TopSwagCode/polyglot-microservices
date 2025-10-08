package application

import (
	"context"
	"fmt"

	"github.com/topswagcode/task-service/internal/domain/task"
	"github.com/topswagcode/task-service/internal/infrastructure/kafka"
)

type ProjectAccessor interface { Get(ctx context.Context, id uint, userID string) (bool, error) }

type TaskService struct {
	repo        task.Repository
	projects    ProjectAccessor
	producer    kafka.Producer
}

func NewTaskService(r task.Repository, pa ProjectAccessor, p kafka.Producer) *TaskService { return &TaskService{repo: r, projects: pa, producer: p} }

func (s *TaskService) Create(ctx context.Context, title, desc string, projectID uint, priority, userID, username string) (*task.Task, error) {
	if title == "" { return nil, fmt.Errorf("title required") }
	if priority == "" { priority = task.PriorityMedium }
	if ok, err := s.projects.Get(ctx, projectID, userID); err != nil || !ok { return nil, fmt.Errorf("project access denied") }
	t := &task.Task{Title: title, Description: desc, ProjectID: projectID, Status: task.StatusOpen, Priority: priority, UserID: userID, Username: username}
	if err := s.repo.Create(ctx, t); err != nil { return nil, err }
	if s.producer != nil { _ = s.producer.TaskCreated(ctx, t.ID, t.ProjectID, t.Title, t.Status, userID, username) }
	return t, nil
}

func (s *TaskService) Get(ctx context.Context, id uint, userID string) (*task.Task, error) { return s.repo.GetByID(ctx, id, userID) }
func (s *TaskService) List(ctx context.Context, userID string) ([]task.Task, error) { return s.repo.ListByUser(ctx, userID) }
func (s *TaskService) ListByProject(ctx context.Context, projectID uint, userID string) ([]task.Task, error) { return s.repo.ListByProject(ctx, projectID, userID) }

func (s *TaskService) Update(ctx context.Context, id uint, title, desc, status, priority, userID, username string) (*task.Task, error) {
	t, err := s.repo.GetByID(ctx, id, userID)
	if err != nil { return nil, err }
	if title != "" { t.Title = title }
	if desc != "" { t.Description = desc }
	if status != "" { t.Status = status }
	if priority != "" { t.Priority = priority }
	if err := s.repo.Update(ctx, t); err != nil { return nil, err }
	if s.producer != nil { _ = s.producer.TaskUpdated(ctx, t.ID, t.ProjectID, t.Title, t.Status, userID, username) }
	return t, nil
}
