package api

import (
	"net/http"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/topswagcode/task-service/internal/api/handlers"
)

type Router struct { r *chi.Mux }

func NewRouter(projectH *handlers.ProjectHandler, taskH *handlers.TaskHandler) *Router {
	mux := chi.NewRouter()
	mux.Use(middleware.RequestID, middleware.Recoverer, middleware.Logger)
	// JSON content type middleware
	mux.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Let health endpoint stay plain text quickly
			if r.URL.Path == "/health" { next.ServeHTTP(w, r); return }
			w.Header().Set("Content-Type", "application/json; charset=utf-8")
			next.ServeHTTP(w, r)
		})
	})
	mux.Get("/health", func(w http.ResponseWriter, r *http.Request) { w.Header().Set("Content-Type", "text/plain; charset=utf-8"); w.Write([]byte("ok")) })
	mux.Route("/projects", func(r chi.Router) {
		r.Get("/", projectH.List)
		r.Post("/", projectH.Create)
		r.Get("/{id}", projectH.Get)
	})
	mux.Route("/tasks", func(r chi.Router) {
		r.Get("/", taskH.List)
		r.Post("/", taskH.Create)
		r.Get("/{id}", taskH.Get)
		r.Put("/{id}", taskH.Update)
	})
	return &Router{r: mux}
}

func (rt *Router) Handler() http.Handler { return rt.r }
