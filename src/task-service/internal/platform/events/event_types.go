package events

import "fmt"

// ---- Project Events ----

type ProjectCreated struct {
	ID uint
	ProjectName string
	UserID string
	Username string
}

func (e ProjectCreated) Name() string { return "project.created" }
func (e ProjectCreated) Key() string { return fmt.Sprintf("project:%d", e.ID) }
func (e ProjectCreated) Payload() interface{} { return e }

// ---- Task Events ----

type TaskCreated struct {
	ID uint
	ProjectID uint
	Title string
	Status string
	UserID string
	Username string
}

func (e TaskCreated) Name() string { return "task.created" }
func (e TaskCreated) Key() string { return fmt.Sprintf("task:%d", e.ID) }
func (e TaskCreated) Payload() interface{} { return e }

type TaskUpdated struct {
	ID uint
	ProjectID uint
	Title string
	Status string
	UserID string
	Username string
}

func (e TaskUpdated) Name() string { return "task.updated" }
func (e TaskUpdated) Key() string { return fmt.Sprintf("task:%d", e.ID) }
func (e TaskUpdated) Payload() interface{} { return e }
