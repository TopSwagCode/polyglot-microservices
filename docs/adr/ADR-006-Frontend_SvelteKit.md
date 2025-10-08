# ADR 6: Implement Frontend Using SvelteKit

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
Initially, the project was designed purely as a backend and API-based proof of concept to demonstrate microservices and event-driven architecture.  
However, it became clear that having a **visual frontend** would make it much easier to demo and explain how different services interact in real time.  
The frontend provides a way to visualize system activity, interact with APIs, and present analytics data in a user-friendly way.

## Decision
We decided to build the **frontend using Svelte and SvelteKit**.  
SvelteKit has become the preferred frontend framework due to its simplicity, elegant syntax, and close resemblance to plain HTML and JavaScript.  
It offers flexibility to deploy as a static site or enable server-side rendering (SSR), depending on future requirements.  
The choice also aligns with the project’s theme of showcasing multiple technologies across different layers of the system.

## Consequences

- ✅ Provides a clean, fast, and lightweight frontend for demos and visualization.  
- ✅ Easy to learn and maintain thanks to Svelte’s minimal syntax.  
- ✅ Demonstrates flexibility between static and server-side rendering modes.  
- ❌ Smaller ecosystem compared to React or Angular.  
- ❌ Requires some additional setup to integrate with the existing backend APIs securely.

## Alternatives Considered

- **Blazor / WebAssembly**: Rejected because two services (API Gateway and Auth) were already implemented in .NET, and the goal was to diversify the tech stack and showcase new tools.
