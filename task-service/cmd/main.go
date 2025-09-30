package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/topswagcode/task-service/internal/api"
	"github.com/topswagcode/task-service/internal/db"
	"github.com/topswagcode/task-service/internal/events"
	"github.com/topswagcode/task-service/internal/services"
)

func main() {
	// Initialize structured logger
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	slog.Info("Starting Task Service")

	// Initialize database
	database, err := db.New()
	if err != nil {
		slog.Error("Failed to initialize database", "error", err)
		os.Exit(1)
	}
	defer database.Close()

	// Initialize Kafka producer (optional - continues without it if Kafka is unavailable)
	producer, err := events.NewProducer()
	if err != nil {
		slog.Warn("Failed to initialize Kafka producer, continuing without events", "error", err)
		producer = nil
	}
	if producer != nil {
		defer producer.Close()
	}

	// Initialize services
	taskService := services.New(database, producer)

	// Initialize handlers
	handler := api.New(taskService)

	// Setup router
	r := chi.NewRouter()

	// Middleware
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)

	// CORS configuration
	r.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token", "X-User-Id", "X-Username"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300,
	}))

	// Routes
	r.Route("/", func(r chi.Router) {
		// Health check
		r.Get("/health", handler.HealthCheck)

		// Projects
		r.Route("/projects", func(r chi.Router) {
			r.Get("/", handler.GetProjects)
			r.Post("/", handler.CreateProject)
			r.Get("/{id}", handler.GetProject)
		})

		// Tasks
		r.Route("/tasks", func(r chi.Router) {
			r.Get("/", handler.GetTasks)         // Can filter by ?project_id=X
			r.Post("/", handler.CreateTask)
			r.Get("/{id}", handler.GetTask)
			r.Put("/{id}", handler.UpdateTask)
		})
	})

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	server := &http.Server{
		Addr:    ":" + port,
		Handler: r,
	}

	// Start server in a goroutine
	go func() {
		slog.Info("Task Service starting", "port", port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed {
			slog.Error("Server failed to start", "error", err)
			os.Exit(1)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	slog.Info("Shutting down Task Service...")

	// Give outstanding requests 30 seconds to complete
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		slog.Error("Server forced to shutdown", "error", err)
		os.Exit(1)
	}

	slog.Info("Task Service stopped")
}