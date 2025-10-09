package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/topswagcode/task-service/internal/application"
	"github.com/topswagcode/task-service/internal/domain/task"
)

type TaskHandler struct { svc *application.TaskService }

func NewTaskHandler(s *application.TaskService) *TaskHandler { return &TaskHandler{svc: s} }

func (h *TaskHandler) Create(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); username := r.Header.Get("X-Username")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	var body struct { Title, Description, Priority string; ProjectID uint `json:"project_id"` }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil { http.Error(w, "bad request", http.StatusBadRequest); return }
	t, err := h.svc.Create(r.Context(), body.Title, body.Description, body.ProjectID, body.Priority, userID, username)
	if err != nil { http.Error(w, err.Error(), http.StatusBadRequest); return }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(map[string]any{"id": t.ID, "title": t.Title, "project_id": t.ProjectID, "status": t.Status, "priority": t.Priority})
}

func (h *TaskHandler) Get(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	idStr := chi.URLParam(r, "id"); id, _ := strconv.ParseUint(idStr, 10, 32)
	t, err := h.svc.Get(r.Context(), uint(id), userID)
	if err != nil { http.Error(w, err.Error(), http.StatusNotFound); return }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(map[string]any{"id": t.ID, "title": t.Title, "project_id": t.ProjectID, "status": t.Status, "priority": t.Priority})
}

func (h *TaskHandler) List(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	projectIDStr := r.URL.Query().Get("project_id")
	if projectIDStr != "" { pid, _ := strconv.ParseUint(projectIDStr, 10, 32); ts, err := h.svc.ListByProject(r.Context(), uint(pid), userID); if err != nil { http.Error(w, err.Error(), http.StatusInternalServerError); return }; h.respondTasks(w, ts); return }
	ts, err := h.svc.List(r.Context(), userID); if err != nil { http.Error(w, err.Error(), http.StatusInternalServerError); return }
	h.respondTasks(w, ts)
}

func (h *TaskHandler) Update(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); username := r.Header.Get("X-Username")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	idStr := chi.URLParam(r, "id"); id, _ := strconv.ParseUint(idStr, 10, 32)
	var body struct { Title, Description, Status, Priority string }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil { http.Error(w, "bad request", http.StatusBadRequest); return }
	t, err := h.svc.Update(r.Context(), uint(id), body.Title, body.Description, body.Status, body.Priority, userID, username)
	if err != nil { http.Error(w, err.Error(), http.StatusInternalServerError); return }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(map[string]any{"id": t.ID, "title": t.Title, "project_id": t.ProjectID, "status": t.Status, "priority": t.Priority})
}

func (h *TaskHandler) respondTasks(w http.ResponseWriter, tasks []task.Task) {
	resp := make([]map[string]any, 0, len(tasks))
	for _, t := range tasks {
		resp = append(resp, map[string]any{"id": t.ID, "title": t.Title, "project_id": t.ProjectID, "status": t.Status, "priority": t.Priority})
	}
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(resp)
}
