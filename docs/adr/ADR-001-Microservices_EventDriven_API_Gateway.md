# ADR 1: Adopt Microservices and Event-Driven Architecture with API Gateway

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
The goal of this project is to create a fun, scalable, and decoupled system that allows flexibility in technology choices. We wanted an architecture that welcomes contributions from various tech stacks while maintaining a cohesive and reliable system. The main challenge was finding a structure that supports scalability, team autonomy, and easy feature integration without creating strong dependencies between components.

## Decision
We decided to adopt a **microservices architecture** combined with an **event-driven system** and an **API Gateway** layer.  
- The **API Gateway** abstracts all backend services from external clients, providing a unified entry point and handling routing, authentication, and throttling.  
- Each feature or service is developed as an independent **microservice**, allowing teams to choose the most suitable language and framework.  
- To ensure decoupling and asynchronous communication, services communicate through **events**, enabling loose coupling and better fault tolerance.

## Consequences

- ✅ Improved scalability — services can scale independently.  
- ✅ Flexibility in technology choice for each service.  
- ✅ Fault isolation — issues in one service do not cascade to others.  
- ❌ Increased operational complexity due to managing multiple deployments.  
- ❌ Requires strong observability and monitoring to track cross-service events.

## Alternatives Considered

- **Monolithic Architecture**: Rejected due to difficulty scaling and maintaining flexibility for different tech stacks.  
- **Modular Monolith**: Rejected because it still creates tight coupling between modules, which would limit independent scaling and deployments.
