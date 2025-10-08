package handlers

import (
	"encoding/json"
	"net/http"

	"github.com/topswagcode/task-service/internal/http/dto"
	"github.com/topswagcode/task-service/internal/project"
)

type ProjectHandlers struct { svc *project.Service }

func NewProjectHandlers(s *project.Service) *ProjectHandlers { return &ProjectHandlers{svc: s} }

func (h *ProjectHandlers) Create(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	username := r.Header.Get("X-Username")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	var req dto.CreateProjectRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil { http.Error(w, "bad request", http.StatusBadRequest); return }
	p, err := h.svc.Create(r.Context(), req.Name, userID, username)
	if err != nil { http.Error(w, err.Error(), http.StatusBadRequest); return }
	json.NewEncoder(w).Encode(dto.ProjectResponse{ID: p.ID, Name: p.Name})
}

func (h *ProjectHandlers) Get(w http.ResponseWriter, r *http.Request, id uint) {
	userID := r.Header.Get("X-User-Id")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	p, err := h.svc.Get(r.Context(), id, userID)
	if err != nil { status := http.StatusInternalServerError; if err == project.ErrNotFound { status = http.StatusNotFound }; http.Error(w, err.Error(), status); return }
	json.NewEncoder(w).Encode(dto.ProjectResponse{ID: p.ID, Name: p.Name})
}

func (h *ProjectHandlers) List(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	ps, err := h.svc.List(r.Context(), userID)
	if err != nil { http.Error(w, err.Error(), http.StatusInternalServerError); return }
	resp := make([]dto.ProjectResponse, 0, len(ps))
	for _, p := range ps { resp = append(resp, dto.ProjectResponse{ID: p.ID, Name: p.Name}) }
	json.NewEncoder(w).Encode(resp)
}
