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
	"github.com/topswagcode/task-service/internal/api"
	"github.com/topswagcode/task-service/internal/api/handlers"
	"github.com/topswagcode/task-service/internal/application"
	"github.com/topswagcode/task-service/internal/infrastructure/db"
	"github.com/topswagcode/task-service/internal/infrastructure/kafka"
	"github.com/topswagcode/task-service/pkg/config"
	"github.com/topswagcode/task-service/pkg/logger"
)

type projectAccessor struct { svc *application.ProjectService }
func (a *projectAccessor) Get(ctx context.Context, id uint, userID string) (bool, error) {
	p, err := a.svc.Get(ctx, id, userID)
	if err != nil { return false, err }
	return p != nil, nil
}

func main() {
	log := logger.New()
	slog.SetDefault(log)
	cfg := config.Load()

	database, err := db.New()
	if err != nil { log.Error("db init failed", "error", err); os.Exit(1) }
	defer database.Close()

	producer, err := kafka.NewKafkaProducer()
	if err != nil { log.Warn("kafka disabled", "error", err); producer = nil }
	if producer != nil { defer producer.Close() }

	projRepo := db.NewProjectRepository(database.DB)
	taskRepo := db.NewTaskRepository(database.DB)

	projSvc := application.NewProjectService(projRepo, producer)
	projAccessor := &projectAccessor{svc: projSvc}
	taskSvc := application.NewTaskService(taskRepo, projAccessor, producer)

	projectHandler := handlers.NewProjectHandler(projSvc)
	taskHandler := handlers.NewTaskHandler(taskSvc)
	router := api.NewRouter(projectHandler, taskHandler)

	corsMw := cors.Handler(cors.Options{AllowedOrigins: []string{"*"}, AllowedMethods: []string{"GET","POST","PUT","DELETE","OPTIONS"}, AllowedHeaders: []string{"Accept","Authorization","Content-Type","X-User-Id","X-Username"}})
	server := &http.Server{Addr: ":" + cfg.Port, Handler: corsMw(router.Handler())}

	go func(){
		log.Info("api starting", "port", cfg.Port)
		if err := server.ListenAndServe(); err != nil && err != http.ErrServerClosed { log.Error("server error", "error", err); os.Exit(1) }
	}()

	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second); defer cancel()
	if err := server.Shutdown(ctx); err != nil { log.Error("graceful shutdown failed", "error", err); os.Exit(1) }
	log.Info("stopped")
}
