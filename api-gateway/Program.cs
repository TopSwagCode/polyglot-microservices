using System.Text;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;

var builder = WebApplication.CreateBuilder(args);

// Add JWT Authentication
var jwtKey = builder.Configuration["Jwt:Key"] ?? "supersecretkey";
var jwtIssuer = builder.Configuration["Jwt:Issuer"] ?? "auth-service";
var jwtAudience = builder.Configuration["Jwt:Audience"] ?? "polyglot-platform";

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = jwtIssuer,
            ValidAudience = jwtAudience,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(jwtKey))
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("authenticated", policy =>
        policy.RequireAuthenticatedUser());
});

// Add YARP
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

// Add health checks
builder.Services.AddHealthChecks();

// Add CORS for development
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseCors("AllowAll");
}

// Add a simple health check endpoint
app.MapGet("/health", () => "API Gateway is healthy");

// Add a root endpoint that shows available routes
app.MapGet("/", () => new
{
    Service = "API Gateway",
    Version = "1.0.0",
    Routes = new[]
    {
        "/auth/* -> Auth Service",
        "/tasks/* -> Task Service (requires authentication)",
        "/projects/* -> Task Service (requires authentication)",
        "/analytics/* -> Analytics Service (requires authentication)",
        "/health -> Health Check"
    }
});

app.UseAuthentication();
app.UseAuthorization();

// Add middleware for role-based access control and header enrichment
app.MapReverseProxy(proxyPipeline =>
{
    proxyPipeline.Use(async (context, next) =>
    {
        // Check if this is an analytics request Maybe make something else only for admins :)
        // if (context.Request.Path.StartsWithSegments("/analytics"))
        // {
        //     // Analytics endpoints require Admin role
        //     if (!context.User.IsInRole("Admin"))
        //     {
        //         context.Response.StatusCode = StatusCodes.Status403Forbidden;
        //         await context.Response.WriteAsync("Forbidden: Admin role required for analytics endpoints");
        //         return;
        //     }
        // }

        // Add headers for authenticated users
        if (context.User.Identity?.IsAuthenticated == true)
        {
            // Extract user information from JWT claims
            var userId = context.User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value ?? 
                        context.User.FindFirst("nameid")?.Value ?? 
                        context.User.FindFirst("sub")?.Value;
            var username = context.User.Identity.Name ?? 
                          context.User.FindFirst("unique_name")?.Value ?? 
                          context.User.FindFirst(System.Security.Claims.ClaimTypes.Name)?.Value;
            var role = context.User.FindFirst(System.Security.Claims.ClaimTypes.Role)?.Value;

            // Add custom headers for downstream services
            if (!string.IsNullOrEmpty(userId))
            {
                context.Request.Headers["X-User-Id"] = userId;
            }

            if (!string.IsNullOrEmpty(username))
            {
                context.Request.Headers["X-Username"] = username;
            }

            if (!string.IsNullOrEmpty(role))
            {
                context.Request.Headers["X-User-Role"] = role;
            }

            // Log for debugging
            app.Logger.LogInformation("Enriching request with user headers: UserId={UserId}, Username={Username}, Role={Role}", 
                userId, username, role);
        }

        await next();
    });
});

app.Run();
