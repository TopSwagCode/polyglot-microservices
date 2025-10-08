# Planning: Analytics Service with Admin Role (via API Gateway)

This document extends the Analytics Service and API Gateway planning
with **role-based access control (RBAC)**.\
Only users with the **Admin** role can access analytics endpoints.

------------------------------------------------------------------------

## 🔹 Goals

-   Add **role-based authentication** with seeded `admin/admin` user in
    **Auth Service**.
-   Only **Admin** users can call Analytics endpoints.
-   API Gateway checks user role before forwarding requests to Analytics
    Service.
-   Analytics Service trusts the Gateway and does not perform additional
    role validation.

------------------------------------------------------------------------

## 🔹 Auth Service Updates

1.  Extend **User model** with a `Role` field:

``` csharp
public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string PasswordHash { get; set; } = string.Empty;
    public string Role { get; set; } = "User"; // Default role
}
```

2.  Seed a default **Admin** user:

``` csharp
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();

    if (!db.Users.Any(u => u.Username == "admin"))
    {
        var adminUser = new User
        {
            Username = "admin",
            PasswordHash = BCrypt.Net.BCrypt.HashPassword("admin"),
            Role = "Admin"
        };
        db.Users.Add(adminUser);
        db.SaveChanges();
    }
}
```

3.  Include `Role` in JWT claims:

``` csharp
var claims = new[]
{
    new Claim(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
    new Claim(ClaimTypes.Name, user.Username),
    new Claim(ClaimTypes.Role, user.Role)
};
```

------------------------------------------------------------------------

## 🔹 API Gateway Updates

-   API Gateway enforces **Admin role** for Analytics routes before
    forwarding.

### Example YARP + Role Check

``` csharp
app.MapReverseProxy(proxyPipeline =>
{
    proxyPipeline.Use(async (context, next) =>
    {
        if (context.Request.Path.StartsWithSegments("/analytics"))
        {
            if (!context.User.IsInRole("Admin"))
            {
                context.Response.StatusCode = StatusCodes.Status403Forbidden;
                await context.Response.WriteAsync("Forbidden: Admin role required");
                return;
            }
        }

        // Enrich headers
        var userId = context.User.FindFirst("sub")?.Value;
        var username = context.User.Identity?.Name;
        var role = context.User.FindFirst(ClaimTypes.Role)?.Value;

        if (!string.IsNullOrEmpty(userId))
            context.Request.Headers["X-User-Id"] = userId;
        if (!string.IsNullOrEmpty(username))
            context.Request.Headers["X-Username"] = username;
        if (!string.IsNullOrEmpty(role))
            context.Request.Headers["X-User-Role"] = role;

        await next();
    });
});
```

------------------------------------------------------------------------

## 🔹 Analytics Service Updates

-   Trust that the Gateway blocks non-admins.\
-   Optionally check the `X-User-Role` header to confirm.

**Example**

``` python
from fastapi import APIRouter, Request, HTTPException

router = APIRouter()

@router.get("/analytics/tasks-per-user")
async def tasks_per_user(request: Request):
    role = request.headers.get("X-User-Role")
    if role != "Admin":
        raise HTTPException(status_code=403, detail="Forbidden: Admin role required")

    cursor = request.app.state.db.tasks_per_user.find()
    results = []
    async for doc in cursor:
        results.append(doc)
    return {"results": results}
```

------------------------------------------------------------------------

## 🔹 Docker Compose Considerations

-   No changes needed, but make sure only **API Gateway** exposes
    ports.\
-   Auth Service now has a seeded **admin/admin** user.

------------------------------------------------------------------------

## 🔹 Security Considerations

-   Analytics endpoints must be **strictly admin-only**.\
-   Gateway ensures no regular users can access Analytics Service.\
-   Analytics Service still double-checks the `X-User-Role` header for
    defense-in-depth.

------------------------------------------------------------------------

## 🔹 Next Steps

-   Add ability to assign roles dynamically (not just seeded users).\
-   Add an `/auth/users` endpoint to allow role management
    (admin-only).\
-   Add integration tests: ensure non-admins cannot access analytics.
