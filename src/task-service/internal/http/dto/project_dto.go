package dto

// CreateProjectRequest represents incoming JSON for project creation.
type CreateProjectRequest struct { Name string `json:"name"` }

// ProjectResponse shape (kept simple; could map domain to DTO explicitly later).
type ProjectResponse struct {
	ID   uint   `json:"id"`
	Name string `json:"name"`
}
