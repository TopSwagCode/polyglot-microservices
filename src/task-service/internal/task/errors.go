package task

import "errors"

var (
	ErrNotFound = errors.New("task not found")
	ErrProjectAccess = errors.New("project not found or access denied")
)
