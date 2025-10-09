package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/topswagcode/task-service/internal/http/dto"
	"github.com/topswagcode/task-service/internal/task"
)

type TaskHandlers struct{ svc *task.Service }

func NewTaskHandlers(s *task.Service) *TaskHandlers { return &TaskHandlers{svc: s} }

func (h *TaskHandlers) Create(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	username := r.Header.Get("X-Username")
	if userID == "" {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	var req dto.CreateTaskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	t, err := h.svc.Create(r.Context(), req.Title, req.Description, req.ProjectID, req.Priority, userID, username)
	if err != nil {
		status := http.StatusBadRequest
		if err == task.ErrProjectAccess {
			status = http.StatusNotFound
		}
		http.Error(w, err.Error(), status)
		return
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(dto.TaskResponse{ID: t.ID, Title: t.Title, ProjectID: t.ProjectID, Status: t.Status, Priority: t.Priority})
}

func (h *TaskHandlers) Get(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	if userID == "" {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	idStr := chi.URLParam(r, "id")
	id, _ := strconv.ParseUint(idStr, 10, 32)
	t, err := h.svc.Get(r.Context(), uint(id), userID)
	if err != nil {
		status := http.StatusInternalServerError
		if err == task.ErrNotFound {
			status = http.StatusNotFound
		}
		http.Error(w, err.Error(), status)
		return
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(dto.TaskResponse{ID: t.ID, Title: t.Title, ProjectID: t.ProjectID, Status: t.Status, Priority: t.Priority})
}

func (h *TaskHandlers) List(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	if userID == "" {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	projectIDStr := r.URL.Query().Get("project_id")
	if projectIDStr != "" {
		pid, _ := strconv.ParseUint(projectIDStr, 10, 32)
		ts, err := h.svc.ListByProject(r.Context(), uint(pid), userID)
		if err != nil {
			status := http.StatusInternalServerError
			if err == task.ErrProjectAccess {
				status = http.StatusNotFound
			}
			http.Error(w, err.Error(), status)
			return
		}
		resp := make([]dto.TaskResponse, 0, len(ts))
		for _, t := range ts {
			resp = append(resp, dto.TaskResponse{ID: t.ID, Title: t.Title, ProjectID: t.ProjectID, Status: t.Status, Priority: t.Priority})
		}
		w.Header().Set("Content-Type", "application/json; charset=utf-8")
		json.NewEncoder(w).Encode(resp)
		return
	}
	ts, err := h.svc.List(r.Context(), userID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	resp := make([]dto.TaskResponse, 0, len(ts))
	for _, t := range ts {
		resp = append(resp, dto.TaskResponse{ID: t.ID, Title: t.Title, ProjectID: t.ProjectID, Status: t.Status, Priority: t.Priority})
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(resp)
}

func (h *TaskHandlers) Update(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	username := r.Header.Get("X-Username")
	if userID == "" {
		http.Error(w, "unauthorized", http.StatusUnauthorized)
		return
	}
	idStr := chi.URLParam(r, "id")
	id, _ := strconv.ParseUint(idStr, 10, 32)
	var req dto.UpdateTaskRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}
	t, err := h.svc.Update(r.Context(), uint(id), req.Title, req.Description, req.Status, req.Priority, userID, username)
	if err != nil {
		status := http.StatusInternalServerError
		if err == task.ErrNotFound {
			status = http.StatusNotFound
		}
		http.Error(w, err.Error(), status)
		return
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(dto.TaskResponse{ID: t.ID, Title: t.Title, ProjectID: t.ProjectID, Status: t.Status, Priority: t.Priority})
}
