using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using VehicleService.Infrastructure;
using VehicleService.Infrastructure.Data;
using static VehicleService.Infrastructure.Data.DatabaseSeeder;
using VehicleService.Api.BackgroundServices;

var builder = WebApplication.CreateBuilder(args);

// --------------------------------------------------
// 🔹 Add Services
// --------------------------------------------------

// Add controllers
builder.Services.AddControllers();

// Add Heartbeat Service
builder.Services.AddHostedService<HeartbeatService>();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        var corsOrigins = builder.Configuration["CORS_ORIGINS"] ?? "*";
        if (corsOrigins == "*")
        {
            policy.AllowAnyOrigin()
                  .AllowAnyMethod()
                  .AllowAnyHeader();
        }
        else
        {
            policy.WithOrigins(corsOrigins.Split(','))
                  .AllowAnyMethod()
                  .AllowAnyHeader()
                  .AllowCredentials();
        }
    });
});

// Add Swagger (OpenAPI)
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Vehicle Service API",
        Version = "v1",
        Description = "Fleet Management Vehicle Service API - manages vehicles, maintenance, and dispatch info."
    });
    
    // Add Security Definition
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\"",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// Add Authentication
builder.Services.AddAuthentication("Bearer")
    .AddJwtBearer("Bearer", options =>
    {
        options.Authority = builder.Configuration["Authentication:JwtBearer:Authority"];
        options.Audience = builder.Configuration["Authentication:JwtBearer:Audience"];
        options.RequireHttpsMetadata = bool.Parse(builder.Configuration["Authentication:JwtBearer:RequireHttpsMetadata"] ?? "false");
        
        // Development mode: If Authority is not reachable, don't crash on startup, but requests will fail validation
        // In .NET 7+, validation happens at request time.
        
        options.TokenValidationParameters = new Microsoft.IdentityModel.Tokens.TokenValidationParameters
        {
            ValidateAudience = false, // Allow if audience is not strictly set in token
            ValidateIssuer = true,
            ValidateLifetime = true,
        };
        
        // Handle events if needed for debugging
        options.Events = new Microsoft.AspNetCore.Authentication.JwtBearer.JwtBearerEvents
        {
            OnAuthenticationFailed = context =>
            {
                Console.WriteLine("Authentication Failed: " + context.Exception.Message);
                return Task.CompletedTask;
            }
        };
    });

using Microsoft.AspNetCore.Authorization; // Add this

// Add Authorization with Fallback Policy
builder.Services.AddAuthorization(options =>
{
    // Default Policy: User must be authenticated
    options.FallbackPolicy = new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build();

    // Admin Only Policy
    options.AddPolicy("AdminOnly", policy => 
        policy.RequireAssertion(context => 
            context.User.IsInRole("fleet-admin") || 
            context.User.HasClaim(c => c.Type == "realm_access" && c.Value.Contains("fleet-admin"))
        ));
});

// Add PostgreSQL + Infrastructure Layer (DbContext + Repository)
builder.Services.AddInfrastructure(builder.Configuration);

// --------------------------------------------------
// 🔹 Build the App
// --------------------------------------------------
var app = builder.Build();

// --------------------------------------------------
// 🔹 Middleware Pipeline
// --------------------------------------------------
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c =>
    {
        c.SwaggerEndpoint("/swagger/v1/swagger.json", "Vehicle Service API v1");
        c.RoutePrefix = string.Empty; // Open Swagger at root URL
    });
}

app.UseHttpsRedirection();

// Enable CORS
app.UseCors();

app.UseAuthentication(); // <--- Add this before Authorization
app.UseAuthorization();

// Map controllers
app.MapControllers();

// --------------------------------------------------
// 🔹 Health Check Endpoints
// --------------------------------------------------
// Basic health check for Docker
app.MapGet("/health", () => Results.Ok(new { status = "healthy", service = "vehicle-service" })).AllowAnonymous();

// Database health check
app.MapGet("/health/db", async (VehicleDbContext db) =>
{
    try
    {
        var canConnect = await db.Database.CanConnectAsync();
        return Results.Ok(new { database = "vehicle_db", connected = canConnect });
    }
    catch (Exception ex)
    {
        return Results.Problem(ex.Message);
    }
}).AllowAnonymous();

// Root endpoint
app.MapGet("/", () => "✅ Vehicle Service Running and Healthy!").AllowAnonymous();

// --------------------------------------------------
// 🔹 Database Initialization (Migrations + Seeding)
// --------------------------------------------------
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<VehicleDbContext>();
    var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
    
    try
    {
        // Apply any pending migrations
        logger.LogInformation("🔄 Applying database migrations...");
        await db.Database.MigrateAsync();
        logger.LogInformation("✅ Database migrations applied successfully");
        
        // Seed sample data
        logger.LogInformation("🌱 Checking if database needs seeding...");
        await DatabaseSeeder.SeedAsync(db);
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "❌ An error occurred while initializing the database");
        throw;
    }
}

// --------------------------------------------------
// 🔹 Run the Application
// --------------------------------------------------
app.Run();
