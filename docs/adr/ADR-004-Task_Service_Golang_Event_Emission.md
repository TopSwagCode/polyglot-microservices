# ADR 4: Implement Task Service Using Golang with Event Emission on CRUD Operations

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
The Task Service is responsible for managing basic task-related operations, such as creating, updating, and deleting tasks.  
It also needs to publish events whenever changes occur, allowing other services to react asynchronously (for example, notifications or analytics).  
This service is part of the microservices ecosystem and should be simple, performant, and easy to deploy independently.

## Decision
We decided to implement the **Task Service in Golang (Go)**.  
Golang is known for its strong performance, simplicity, and concurrency support, making it ideal for small, stateless services.  
Additionally, it provides a great opportunity to explore Go in a production-like setup and demonstrate interoperability between different languages within the microservices architecture.

## Consequences

- ✅ High performance and low resource consumption for API operations.  
- ✅ Simple and fast to build and deploy.  
- ✅ Great opportunity to gain experience with Go.  
- ❌ Limited library ecosystem compared to .NET or Node.js in some areas.  
- ❌ Requires maintaining language-specific tooling and CI/CD pipelines.

## Alternatives Considered

- **Rust**: Rejected due to steeper learning curve and slower development speed at this stage. Might be revisited later once the POC stabilizes, as a performance-focused service implementation.
