package services

import (
	"fmt"

	"github.com/topswagcode/task-service/internal/db"
	"github.com/topswagcode/task-service/internal/events"
	"github.com/topswagcode/task-service/internal/models"
	"gorm.io/gorm"
)

// TaskService handles business logic for tasks and projects
type TaskService struct {
	db       *db.Database
	producer *events.Producer
}

// New creates a new task service
func New(database *db.Database, producer *events.Producer) *TaskService {
	return &TaskService{
		db:       database,
		producer: producer,
	}
}

// CreateProject creates a new project
func (s *TaskService) CreateProject(req models.CreateProjectRequest, userID, username string) (*models.Project, error) {
	project := models.Project{
		Name:     req.Name,
		UserID:   userID,
		Username: username,
	}

	if err := s.db.DB.Create(&project).Error; err != nil {
		return nil, fmt.Errorf("failed to create project: %w", err)
	}

	// Publish event
	if s.producer != nil {
		if err := s.producer.PublishProjectEvent(events.EventProjectCreated, project.ID, project.Name, userID, username); err != nil {
			// Log error but don't fail the request
			fmt.Printf("Failed to publish project created event: %v\n", err)
		}
	}

	return &project, nil
}

// GetProject retrieves a project by ID for a specific user
func (s *TaskService) GetProject(id uint, userID string) (*models.Project, error) {
	var project models.Project
	err := s.db.DB.Preload("Tasks").Where("id = ? AND user_id = ?", id, userID).First(&project).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("project not found")
		}
		return nil, fmt.Errorf("failed to get project: %w", err)
	}
	return &project, nil
}

// GetProjects retrieves all projects for a specific user
func (s *TaskService) GetProjects(userID string) ([]models.Project, error) {
	var projects []models.Project
	err := s.db.DB.Where("user_id = ?", userID).Find(&projects).Error
	if err != nil {
		return nil, fmt.Errorf("failed to get projects: %w", err)
	}
	return projects, nil
}

// CreateTask creates a new task
func (s *TaskService) CreateTask(req models.CreateTaskRequest, userID, username string) (*models.Task, error) {
	// Verify project exists and belongs to user
	var project models.Project
	if err := s.db.DB.Where("id = ? AND user_id = ?", req.ProjectID, userID).First(&project).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("project not found or access denied")
		}
		return nil, fmt.Errorf("failed to verify project: %w", err)
	}

	task := models.Task{
		Title:       req.Title,
		Description: req.Description,
		ProjectID:   req.ProjectID,
		Status:      models.TaskStatusOpen,
		Priority:    req.Priority,
		UserID:      userID,
		Username:    username,
	}

	if task.Priority == "" {
		task.Priority = models.TaskPriorityMedium
	}

	if err := s.db.DB.Create(&task).Error; err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}

	// Publish event
	if s.producer != nil {
		if err := s.producer.PublishTaskEvent(events.EventTaskCreated, task.ID, task.ProjectID, task.Title, task.Status, userID, username); err != nil {
			// Log error but don't fail the request
			fmt.Printf("Failed to publish task created event: %v\n", err)
		}
	}

	return &task, nil
}

// GetTask retrieves a task by ID for a specific user
func (s *TaskService) GetTask(id uint, userID string) (*models.Task, error) {
	var task models.Task
	err := s.db.DB.Preload("Project").Where("id = ? AND user_id = ?", id, userID).First(&task).Error
	if err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("task not found")
		}
		return nil, fmt.Errorf("failed to get task: %w", err)
	}
	return &task, nil
}

// GetTasks retrieves all tasks for a specific user
func (s *TaskService) GetTasks(userID string) ([]models.Task, error) {
	var tasks []models.Task
	err := s.db.DB.Preload("Project").Where("user_id = ?", userID).Find(&tasks).Error
	if err != nil {
		return nil, fmt.Errorf("failed to get tasks: %w", err)
	}
	return tasks, nil
}

// GetTasksByProject retrieves all tasks for a specific project and user
func (s *TaskService) GetTasksByProject(projectID uint, userID string) ([]models.Task, error) {
	// First verify the project belongs to the user
	var project models.Project
	if err := s.db.DB.Where("id = ? AND user_id = ?", projectID, userID).First(&project).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("project not found or access denied")
		}
		return nil, fmt.Errorf("failed to verify project: %w", err)
	}

	var tasks []models.Task
	err := s.db.DB.Where("project_id = ? AND user_id = ?", projectID, userID).Find(&tasks).Error
	if err != nil {
		return nil, fmt.Errorf("failed to get tasks: %w", err)
	}
	return tasks, nil
}

// UpdateTask updates an existing task
func (s *TaskService) UpdateTask(id uint, req models.UpdateTaskRequest, userID, username string) (*models.Task, error) {
	var task models.Task
	if err := s.db.DB.Where("id = ? AND user_id = ?", id, userID).First(&task).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			return nil, fmt.Errorf("task not found")
		}
		return nil, fmt.Errorf("failed to find task: %w", err)
	}

	// Update fields
	if req.Title != "" {
		task.Title = req.Title
	}
	if req.Description != "" {
		task.Description = req.Description
	}
	if req.Status != "" {
		task.Status = req.Status
	}
	if req.Priority != "" {
		task.Priority = req.Priority
	}

	if err := s.db.DB.Save(&task).Error; err != nil {
		return nil, fmt.Errorf("failed to update task: %w", err)
	}

	// Publish event
	if s.producer != nil {
		if err := s.producer.PublishTaskEvent(events.EventTaskUpdated, task.ID, task.ProjectID, task.Title, task.Status, userID, username); err != nil {
			// Log error but don't fail the request
			fmt.Printf("Failed to publish task updated event: %v\n", err)
		}
	}

	return &task, nil
}