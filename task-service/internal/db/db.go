package db

import (
	"fmt"
	"log/slog"
	"os"

	"github.com/topswagcode/task-service/internal/models"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

// Database wraps the GORM database connection
type Database struct {
	DB *gorm.DB
}

// New creates a new database connection
func New() (*Database, error) {
	dsn := os.Getenv("DB_DSN")
	if dsn == "" {
		dsn = "host=postgres user=taskuser password=secret dbname=taskdb port=5432 sslmode=disable"
	}

	slog.Info("Connecting to database", "dsn", dsn)

	// Configure GORM logger
	gormConfig := &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	}

	db, err := gorm.Open(postgres.Open(dsn), gormConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to connect to database: %w", err)
	}

	// Test the connection
	sqlDB, err := db.DB()
	if err != nil {
		return nil, fmt.Errorf("failed to get underlying sql.DB: %w", err)
	}

	if err := sqlDB.Ping(); err != nil {
		return nil, fmt.Errorf("failed to ping database: %w", err)
	}

	slog.Info("Database connection established successfully")

	database := &Database{DB: db}

	// Run migrations
	if err := database.Migrate(); err != nil {
		return nil, fmt.Errorf("failed to run migrations: %w", err)
	}

	return database, nil
}

// Migrate runs database migrations
func (d *Database) Migrate() error {
	slog.Info("Running database migrations")

	err := d.DB.AutoMigrate(
		&models.Project{},  
		&models.Task{},
	)
	if err != nil {
		return fmt.Errorf("failed to auto migrate: %w", err)
	}

	slog.Info("Database migrations completed successfully")
	return nil
}

// Close closes the database connection
func (d *Database) Close() error {
	sqlDB, err := d.DB.DB()
	if err != nil {
		return err
	}
	return sqlDB.Close()
}