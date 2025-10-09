package http

import (
	"net/http"
	"strconv"

	"github.com/go-chi/chi/v5"
	ichimw "github.com/go-chi/chi/v5/middleware"
	"github.com/topswagcode/task-service/internal/http/handlers"
)

type Router struct{ mux *chi.Mux }

func NewRouter(ph *handlers.ProjectHandlers, th *handlers.TaskHandlers) *Router {
	mux := chi.NewRouter()
	// Register all middlewares BEFORE any routes (chi requirement)
	mux.Use(ichimw.Logger, ichimw.Recoverer, ichimw.RequestID, ichimw.RealIP)
	// JSON Content-Type middleware for all non-health endpoints
	mux.Use(func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.URL.Path != "/health" {
				// Only set if not already present (handlers may set explicitly)
				if ct := w.Header().Get("Content-Type"); ct == "" {
					w.Header().Set("Content-Type", "application/json; charset=utf-8")
				}
			}
			next.ServeHTTP(w, r)
		})
	})

	// Routes
	mux.Get("/health", handlers.Health)
	mux.Route("/projects", func(r chi.Router) {
		r.Get("/", ph.List)
		r.Post("/", ph.Create)
		r.Get("/{id}", func(w http.ResponseWriter, r *http.Request) {
			idStr := chi.URLParam(r, "id")
			id, _ := strconv.ParseUint(idStr, 10, 32)
			ph.Get(w, r, uint(id))
		})
	})
	mux.Route("/tasks", func(r chi.Router) {
		r.Get("/", th.List)
		r.Post("/", th.Create)
		r.Get("/{id}", th.Get)
		r.Put("/{id}", th.Update)
	})
	return &Router{mux: mux}
}

func (r *Router) Handler() http.Handler { return r.mux }
