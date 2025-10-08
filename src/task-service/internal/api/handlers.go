package api

import (
	"encoding/json"
	"log/slog"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/topswagcode/task-service/internal/models"
	"github.com/topswagcode/task-service/internal/services"
)

// Handler contains the HTTP handlers for the task service
type Handler struct {
	taskService *services.TaskService
}

// New creates a new handler
func New(taskService *services.TaskService) *Handler {
	return &Handler{
		taskService: taskService,
	}
}

// getUserInfo extracts user information from headers set by API Gateway
func (h *Handler) getUserInfo(r *http.Request) (userID, username string) {
	userID = r.Header.Get("X-User-Id")
	username = r.Header.Get("X-Username")
	return userID, username
}

// respondJSON sends a JSON response
func (h *Handler) respondJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	if data != nil {
		json.NewEncoder(w).Encode(data)
	}
}

// respondError sends an error response
func (h *Handler) respondError(w http.ResponseWriter, status int, message string) {
	h.respondJSON(w, status, map[string]string{"error": message})
}

// CreateProject handles POST /projects
func (h *Handler) CreateProject(w http.ResponseWriter, r *http.Request) {
	userID, username := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	var req models.CreateProjectRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if req.Name == "" {
		h.respondError(w, http.StatusBadRequest, "Project name is required")
		return
	}

	project, err := h.taskService.CreateProject(req, userID, username)
	if err != nil {
		slog.Error("Failed to create project", "error", err, "userID", userID)
		h.respondError(w, http.StatusInternalServerError, "Failed to create project")
		return
	}

	h.respondJSON(w, http.StatusCreated, project)
}

// GetProject handles GET /projects/{id}
func (h *Handler) GetProject(w http.ResponseWriter, r *http.Request) {
	userID, _ := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	idStr := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid project ID")
		return
	}

	project, err := h.taskService.GetProject(uint(id), userID)
	if err != nil {
		if err.Error() == "project not found" {
			h.respondError(w, http.StatusNotFound, "Project not found")
			return
		}
		slog.Error("Failed to get project", "error", err, "userID", userID, "projectID", id)
		h.respondError(w, http.StatusInternalServerError, "Failed to get project")
		return
	}

	h.respondJSON(w, http.StatusOK, project)
}

// GetProjects handles GET /projects
func (h *Handler) GetProjects(w http.ResponseWriter, r *http.Request) {
	userID, _ := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	projects, err := h.taskService.GetProjects(userID)
	if err != nil {
		slog.Error("Failed to get projects", "error", err, "userID", userID)
		h.respondError(w, http.StatusInternalServerError, "Failed to get projects")
		return
	}

	h.respondJSON(w, http.StatusOK, projects)
}

// CreateTask handles POST /tasks
func (h *Handler) CreateTask(w http.ResponseWriter, r *http.Request) {
	userID, username := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	var req models.CreateTaskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	if req.Title == "" {
		h.respondError(w, http.StatusBadRequest, "Task title is required")
		return
	}

	if req.ProjectID == 0 {
		h.respondError(w, http.StatusBadRequest, "Project ID is required")
		return
	}

	task, err := h.taskService.CreateTask(req, userID, username)
	if err != nil {
		if err.Error() == "project not found or access denied" {
			h.respondError(w, http.StatusNotFound, "Project not found or access denied")
			return
		}
		slog.Error("Failed to create task", "error", err, "userID", userID)
		h.respondError(w, http.StatusInternalServerError, "Failed to create task")
		return
	}

	h.respondJSON(w, http.StatusCreated, task)
}

// GetTask handles GET /tasks/{id}
func (h *Handler) GetTask(w http.ResponseWriter, r *http.Request) {
	userID, _ := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	idStr := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid task ID")
		return
	}

	task, err := h.taskService.GetTask(uint(id), userID)
	if err != nil {
		if err.Error() == "task not found" {
			h.respondError(w, http.StatusNotFound, "Task not found")
			return
		}
		slog.Error("Failed to get task", "error", err, "userID", userID, "taskID", id)
		h.respondError(w, http.StatusInternalServerError, "Failed to get task")
		return
	}

	h.respondJSON(w, http.StatusOK, task)
}

// GetTasks handles GET /tasks
func (h *Handler) GetTasks(w http.ResponseWriter, r *http.Request) {
	userID, _ := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	// Check if filtering by project
	projectIDStr := r.URL.Query().Get("project_id")
	if projectIDStr != "" {
		projectID, err := strconv.ParseUint(projectIDStr, 10, 32)
		if err != nil {
			h.respondError(w, http.StatusBadRequest, "Invalid project ID")
			return
		}

		tasks, err := h.taskService.GetTasksByProject(uint(projectID), userID)
		if err != nil {
			if err.Error() == "project not found or access denied" {
				h.respondError(w, http.StatusNotFound, "Project not found or access denied")
				return
			}
			slog.Error("Failed to get tasks by project", "error", err, "userID", userID, "projectID", projectID)
			h.respondError(w, http.StatusInternalServerError, "Failed to get tasks")
			return
		}

		h.respondJSON(w, http.StatusOK, tasks)
		return
	}

	tasks, err := h.taskService.GetTasks(userID)
	if err != nil {
		slog.Error("Failed to get tasks", "error", err, "userID", userID)
		h.respondError(w, http.StatusInternalServerError, "Failed to get tasks")
		return
	}

	h.respondJSON(w, http.StatusOK, tasks)
}

// UpdateTask handles PUT /tasks/{id}
func (h *Handler) UpdateTask(w http.ResponseWriter, r *http.Request) {
	userID, username := h.getUserInfo(r)
	if userID == "" {
		h.respondError(w, http.StatusUnauthorized, "User not authenticated")
		return
	}

	idStr := chi.URLParam(r, "id")
	id, err := strconv.ParseUint(idStr, 10, 32)
	if err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid task ID")
		return
	}

	var req models.UpdateTaskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		h.respondError(w, http.StatusBadRequest, "Invalid request body")
		return
	}

	task, err := h.taskService.UpdateTask(uint(id), req, userID, username)
	if err != nil {
		if err.Error() == "task not found" {
			h.respondError(w, http.StatusNotFound, "Task not found")
			return
		}
		slog.Error("Failed to update task", "error", err, "userID", userID, "taskID", id)
		h.respondError(w, http.StatusInternalServerError, "Failed to update task")
		return
	}

	h.respondJSON(w, http.StatusOK, task)
}

// HealthCheck handles GET /health
func (h *Handler) HealthCheck(w http.ResponseWriter, r *http.Request) {
	h.respondJSON(w, http.StatusOK, map[string]string{
		"status":  "healthy",
		"service": "task-service",
		"version": "1.0.0",
	})
}