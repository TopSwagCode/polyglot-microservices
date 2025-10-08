# ADR 2: Adopt .NET YARP as API Gateway

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** TopSwagCode

## Context
As discussed in the previous ADR, the project architecture is designed to keep APIs decoupled from external clients. The API Gateway serves as the unified entry point for all client interactions, handling routing, authentication, rate limiting, and request forwarding to internal microservices.  
The goal was to choose a gateway solution that offers flexibility, customization, and the opportunity to experiment with modern .NET technologies.

## Decision
We decided to adopt **.NET YARP (Yet Another Reverse Proxy)** as the project's API Gateway.  
The primary motivation was to explore and demonstrate YARP’s extensibility and seamless integration within the .NET ecosystem.  
While tools like **Kong** and **Traefik** are more mature and production-proven, YARP provides a highly customizable, code-first approach that aligns with the project's experimental and educational goals.

## Consequences

- ✅ Enables deep customization and integration with .NET middleware and services.  
- ✅ Lightweight and easy to embed within existing .NET projects.  
- ✅ Provides hands-on learning opportunity with modern Microsoft technologies.  
- ❌ Less mature ecosystem compared to established gateways like Kong or Traefik.  
- ❌ May require additional effort for scaling, observability, and plugin-equivalent features.

## Alternatives Considered

- **Kong**: Rejected due to limited flexibility for code-level customization and reliance on plugin-based configuration.  
- **Traefik**: Rejected as it offers fewer opportunities for demonstrating .NET integration and custom behavior within the gateway itself.
