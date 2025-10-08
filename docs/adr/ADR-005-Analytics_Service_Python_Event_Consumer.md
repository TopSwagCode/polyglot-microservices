# ADR 5: Implement Analytics Service Using Python as Event-Driven Consumer

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
The Analytics Service is designed as a **decoupled component** that operates entirely from the event stream.  
It listens to events published by other services (for example, the Task Service) and performs basic analytics to derive insights such as activity trends, task completions, or user engagement.  
The goal is to illustrate how a completely separate team or service could work independently — consuming shared events rather than directly calling other APIs.  
This service further demonstrates the flexibility and scalability of the event-driven architecture adopted in the system.

## Decision
We decided to implement the **Analytics Service in Python**.  
Python was chosen because it is one of the most popular programming languages, widely used in data processing, analytics, and machine learning.  
This also helps highlight the multi-language nature of the project — showing how teams can use different stacks to build services that still integrate seamlessly through events.  
The Python implementation will focus on consuming events, storing summarized metrics, and exposing results via a lightweight API.

## Consequences

- ✅ Demonstrates polyglot microservice capabilities using different languages.  
- ✅ Leverages Python’s strong ecosystem for data analysis and processing.  
- ✅ Clear example of event-driven analytics integration.  
- ❌ May introduce additional dependency management and runtime differences.  
- ❌ Potential performance overhead compared to compiled languages like Go.

## Alternatives Considered

- **Go**: Rejected since it was already used in the Task Service, and the goal was to demonstrate diversity in the tech stack.  
- **.NET**: Rejected for this service to better showcase cross-language interoperability in an event-driven environment.
