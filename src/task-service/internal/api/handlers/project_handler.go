package handlers

import (
	"encoding/json"
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/topswagcode/task-service/internal/application"
)

type ProjectHandler struct { svc *application.ProjectService }

func NewProjectHandler(s *application.ProjectService) *ProjectHandler { return &ProjectHandler{svc: s} }

func (h *ProjectHandler) Create(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); username := r.Header.Get("X-Username")
	if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	var body struct { Name string `json:"name"` }
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil { http.Error(w, "bad request", http.StatusBadRequest); return }
	p, err := h.svc.Create(r.Context(), body.Name, userID, username)
	if err != nil { http.Error(w, err.Error(), http.StatusBadRequest); return }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(map[string]any{"id": p.ID, "name": p.Name})
}

func (h *ProjectHandler) Get(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	idStr := chi.URLParam(r, "id"); id, _ := strconv.ParseUint(idStr, 10, 32)
	p, err := h.svc.Get(r.Context(), uint(id), userID)
	if err != nil { http.Error(w, err.Error(), http.StatusNotFound); return }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(map[string]any{"id": p.ID, "name": p.Name})
}

func (h *ProjectHandler) List(w http.ResponseWriter, r *http.Request) {
	userID := r.Header.Get("X-User-Id"); if userID == "" { http.Error(w, "unauthorized", http.StatusUnauthorized); return }
	ps, err := h.svc.List(r.Context(), userID)
	if err != nil { http.Error(w, err.Error(), http.StatusInternalServerError); return }
	resp := make([]map[string]any, 0, len(ps))
	for _, p := range ps { resp = append(resp, map[string]any{"id": p.ID, "name": p.Name}) }
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	json.NewEncoder(w).Encode(resp)
}
