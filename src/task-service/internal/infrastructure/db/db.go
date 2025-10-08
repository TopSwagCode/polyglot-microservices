package db

import (
	"fmt"
	"log/slog"
	"os"

	"github.com/topswagcode/task-service/internal/domain/project"
	"github.com/topswagcode/task-service/internal/domain/task"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

type Database struct { DB *gorm.DB }

func New() (*Database, error) {
	dsn := os.Getenv("DB_DSN")
	if dsn == "" { dsn = "host=postgres user=taskuser password=secret dbname=taskdb port=5432 sslmode=disable" }
	gormConfig := &gorm.Config{ Logger: logger.Default.LogMode(logger.Info) }
	db, err := gorm.Open(postgres.Open(dsn), gormConfig)
	if err != nil { return nil, fmt.Errorf("connect db: %w", err) }
	if sqlDB, err := db.DB(); err != nil { return nil, err } else if err := sqlDB.Ping(); err != nil { return nil, err }
	instance := &Database{DB: db}
	if err := instance.Migrate(); err != nil { return nil, err }
	return instance, nil
}

func (d *Database) Migrate() error {
	slog.Info("running migrations")
	if err := d.DB.AutoMigrate(&project.Project{}, &task.Task{}); err != nil { return fmt.Errorf("auto migrate: %w", err) }
	return nil
}

func (d *Database) Close() error { if sqlDB, err := d.DB.DB(); err == nil { return sqlDB.Close() } else { return err } }
