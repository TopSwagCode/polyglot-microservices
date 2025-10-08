# ADR 3: Implement Authentication Service Using .NET with Bearer Tokens

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
The system requires a simple authentication mechanism to secure API endpoints and demonstrate how external clients interact through the API Gateway.  
The goal was to keep the implementation lightweight and straightforward, focusing on bearer token authentication that could easily integrate with other microservices without introducing unnecessary complexity.  
This decision also serves to illustrate how authentication flows could later evolve into a more complete identity provider setup.

## Decision
We decided to implement the **authentication service using .NET**, leveraging built-in libraries for generating and validating **JWT (Bearer) tokens**.  
This choice was based on familiarity with the .NET ecosystem and the ability to quickly build a minimal, functional authentication service that integrates well with the **YARP-based API Gateway**.  
The focus was on rapid implementation and demonstration rather than providing a fully-fledged identity management system.

## Consequences

- ✅ Quick to implement and easy to maintain for a Proof of Concept (POC).  
- ✅ Seamless integration with other .NET-based services and middleware.  
- ✅ Provides a clean foundation for future expansion into a full OIDC solution.  
- ❌ Lacks advanced features like user federation, refresh tokens, or consent management.  
- ❌ Will require rework if migrating to a dedicated identity provider in the future.

## Alternatives Considered

- **Keycloak**: Rejected due to added complexity and overhead for a POC project.  
- **IdentityServer**: Rejected for now since it would require more setup effort and introduce advanced OIDC flows not needed at this stage.
