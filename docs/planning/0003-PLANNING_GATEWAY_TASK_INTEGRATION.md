# Planning: API Gateway + Task Service Integration

This document describes how the **API Gateway** and **Task Service**
will work together to handle **user identity** and **authorization**.

------------------------------------------------------------------------

## 🔹 Goals

-   API Gateway validates JWT tokens.
-   Gateway enriches downstream requests with **custom headers**:
    -   `X-User-Id` → unique user ID
    -   `X-Username` → username
-   Task Service uses these headers to:
    -   Associate tasks with the creating user.
    -   Enforce filtering so users only see their own tasks.

------------------------------------------------------------------------

## 🔹 API Gateway Responsibilities

-   Validate incoming JWT (signature, expiry, issuer, audience).
-   Extract claims (`sub` = user id, `unique_name` or `name` =
    username).
-   Forward requests to downstream services.
-   Add custom headers to every forwarded request.

### Example Gateway Header Enrichment

``` csharp
app.MapReverseProxy(proxyPipeline =>
{
    proxyPipeline.Use(async (context, next) =>
    {
        if (context.User.Identity?.IsAuthenticated == true)
        {
            var userId = context.User.FindFirst("sub")?.Value;
            var username = context.User.Identity.Name;

            if (!string.IsNullOrEmpty(userId))
                context.Request.Headers["X-User-Id"] = userId;

            if (!string.IsNullOrEmpty(username))
                context.Request.Headers["X-Username"] = username;
        }
        await next().Invoke();
    });
});
```

Resulting request to Task Service:

    POST /tasks
    X-User-Id: 123
    X-Username: alice

------------------------------------------------------------------------

## 🔹 Task Service Responsibilities

-   Trust requests coming from the gateway (secured via Docker network /
    K8s namespace).\
-   Extract `X-User-Id` and `X-Username` from headers.\
-   Store them in the database alongside tasks.\
-   Filter queries by `user_id`.

### Example Task Table

  id   title          project_id   status   user_id   username
  ---- -------------- ------------ -------- --------- ----------
  1    "First Task"   10           open     123       alice
  2    "Another"      11           closed   456       bob

### Handler Logic (Go + Chi)

``` go
func (h *TaskHandler) CreateTask(w http.ResponseWriter, r *http.Request) {
    userId := r.Header.Get("X-User-Id")
    username := r.Header.Get("X-Username")

    var input CreateTaskRequest
    if err := json.NewDecoder(r.Body).Decode(&input); err != nil {
        http.Error(w, err.Error(), http.StatusBadRequest)
        return
    }

    task := Task{
        Title:     input.Title,
        ProjectID: input.ProjectID,
        Status:    "open",
        UserID:    userId,
        Username:  username,
    }

    if err := h.db.Create(&task).Error; err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    w.WriteHeader(http.StatusCreated)
    json.NewEncoder(w).Encode(task)
}
```

### Query Filtering

``` go
func (h *TaskHandler) GetTasks(w http.ResponseWriter, r *http.Request) {
    userId := r.Header.Get("X-User-Id")

    var tasks []Task
    if err := h.db.Where("user_id = ?", userId).Find(&tasks).Error; err != nil {
        http.Error(w, err.Error(), http.StatusInternalServerError)
        return
    }

    json.NewEncoder(w).Encode(tasks)
}
```

------------------------------------------------------------------------

## 🔹 Security Considerations

-   Downstream services must not be exposed publicly --- they only trust
    headers **inside the network**.\
-   If a request bypasses the gateway, headers must be rejected.\
-   Optionally, Task Service can still **validate JWT** as
    defense-in-depth.

------------------------------------------------------------------------

## 🔹 Docker Compose Networking

-   Both API Gateway and Task Service run in the same
    `docker-compose.yml` network.\
-   Only **Gateway exposes ports** to host machine (`8080:5000`).\
-   Task Service only exposes to the Docker network, not to the host.

Example:

``` yaml
  api-gateway:
    build: ./api-gateway
    ports:
      - "8080:5000"
    depends_on:
      - auth-service
      - task-service

  task-service:
    build: ./task-service
    expose:
      - "8080"   # internal only
    depends_on:
      - postgres
```

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add role-based access (e.g., admins can query all tasks).\
-   Add auditing/logging of user IDs in API Gateway.\
-   Implement OpenTelemetry tracing across Gateway → Task Service.
