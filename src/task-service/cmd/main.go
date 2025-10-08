package main

import (
	"context"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/go-chi/cors"
	platformdb "github.com/topswagcode/task-service/internal/db"
	plat "github.com/topswagcode/task-service/internal/platform/events"
	proj "github.com/topswagcode/task-service/internal/project"
	thttp "github.com/topswagcode/task-service/internal/http"
	"github.com/topswagcode/task-service/internal/http/handlers"
	tproj "github.com/topswagcode/task-service/internal/project"
	ttask "github.com/topswagcode/task-service/internal/task"
)

type projectAccessorAdapter struct{ svc interface{ Get(ctx context.Context, id uint, userID string) (*proj.Project, error) } }

func (a *projectAccessorAdapter) Get(ctx context.Context, id uint, userID string) (*ttask.ProjectRef, error) {
	p, err := a.svc.Get(ctx, id, userID)
	if err != nil { return nil, err }
	return &ttask.ProjectRef{ID: p.ID}, nil
}

func main() {
	// Initialize structured logger
	logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{
		Level: slog.LevelInfo,
	}))
	slog.SetDefault(logger)

	slog.Info("Starting Task Service")

	// Initialize database (reusing existing db package for GORM bootstrap)
	database, err := platformdb.New()
	if err != nil {
		slog.Error("Failed to initialize database", "error", err)
		os.Exit(1)
	}
	defer database.Close()

	// Initialize Kafka publisher (optional)
	publisher, err := plat.NewKafkaProducer()
	if err != nil {
		slog.Warn("Kafka publisher unavailable; continuing without events", "error", err)
		publisher = nil
	} else {
		defer publisher.Close()
	}

	// Repositories
	projectRepo := proj.NewGormRepository(database.DB)
	taskRepo := ttask.NewGormRepository(database.DB)

	// Services
	projectService := tproj.NewService(projectRepo, publisher)
	// Provide project accessor adapter
	projectAccessor := &projectAccessorAdapter{svc: projectService}
	taskService := ttask.NewService(taskRepo, publisher, projectAccessor)

	// Handlers
	projectHandlers := handlers.NewProjectHandlers(projectService)
	taskHandlers := handlers.NewTaskHandlers(taskService)

	// Router
	router := thttp.NewRouter(projectHandlers, taskHandlers)

	// CORS configuration (apply to underlying chi router)
	corsMw := cors.Handler(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type", "X-CSRF-Token", "X-User-Id", "X-Username"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: false,
		MaxAge:           300,
	})
	handlerWithCORS := corsMw(router.Handler())

	// Get port from environment or default to 8080
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	server := &http.Server{Addr: ":" + port, Handler: handlerWithCORS}

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