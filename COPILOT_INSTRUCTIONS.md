# GitHub Copilot Instructions

This repository contains a **polyglot microservices platform** built
with **.NET, Go, and Python**.\
To keep contributions consistent and high quality, GitHub Copilot should
follow these guidelines:

------------------------------------------------------------------------

## 🔹 General Guidelines

-   Prefer **clear, maintainable, and idiomatic code** for each
    language.
-   Use **async/await** in .NET and Python when possible.
-   Use **Go concurrency patterns** (goroutines, channels, context)
    where appropriate.
-   Always add **inline comments** for complex logic.
-   Prefer **composition over inheritance**.
-   Write **small, focused functions** (single responsibility).

------------------------------------------------------------------------

## 🔹 .NET (C#)

-   Target **.NET 8**.
-   Use **minimal APIs** where suitable.
-   Use **record types** for DTOs.
-   Use **dependency injection** properly (`IServiceCollection`).
-   For async methods, always use `Task` return types.
-   Use `ILogger<T>` for logging.

**Testing**: Prefer **xUnit** with clear Arrange-Act-Assert style.

------------------------------------------------------------------------

## 🔹 Go

-   Write **idiomatic Go** (follow [Effective
    Go](https://go.dev/doc/effective_go)).
-   Structure code with `cmd/`, `pkg/`, `internal/` folders.
-   Use `context.Context` for cancellation and timeouts.
-   Handle errors explicitly (`if err != nil { ... }`).
-   Avoid global state.
-   Use `log/slog` for structured logging.

**Testing**: Use the standard `testing` package.

------------------------------------------------------------------------

## 🔹 Python

-   Target **Python 3.11+**.
-   Follow **PEP 8** style guidelines.
-   Use **type hints** everywhere.
-   Prefer **FastAPI** for APIs.
-   Use `async` where possible.
-   Use `logging` module for logs, never `print`.

**Testing**: Use **pytest**.

------------------------------------------------------------------------

## 🔹 Documentation

-   Each service must have a **README.md** explaining purpose,
    endpoints, setup.
-   Use **docstrings** in Python, **XML docs** in C#, and **Go doc
    comments** in Go.

------------------------------------------------------------------------

## 🔹 Git / Repo Hygiene

-   Keep commits **small and descriptive**.
-   Always run tests before committing.
-   Ensure code passes **linters/formatters**:
    -   C#: `dotnet format`
    -   Go: `gofmt`, `golangci-lint`
    -   Python: `black`, `flake8`, `mypy`

------------------------------------------------------------------------

## 🔹 Example Prompts for Copilot

When asking Copilot for help, use prompts like: - "Generate a minimal
FastAPI service with JWT authentication." - "Write an xUnit test for the
TaskController in .NET." - "Add a Go function to publish a Kafka message
with retries." - "Generate Prometheus metrics instrumentation for a
Python FastAPI endpoint."

------------------------------------------------------------------------

✅ By following these rules, Copilot should generate **consistent,
professional, and production-ready code** across all services in this
project.
