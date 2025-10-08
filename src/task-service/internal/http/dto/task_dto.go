package dto

type CreateTaskRequest struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	ProjectID   uint   `json:"project_id"`
	Priority    string `json:"priority"`
}

type UpdateTaskRequest struct {
	Title       string `json:"title"`
	Description string `json:"description"`
	Status      string `json:"status"`
	Priority    string `json:"priority"`
}

type TaskResponse struct {
	ID        uint   `json:"id"`
	Title     string `json:"title"`
	ProjectID uint   `json:"project_id"`
	Status    string `json:"status"`
	Priority  string `json:"priority"`
}
