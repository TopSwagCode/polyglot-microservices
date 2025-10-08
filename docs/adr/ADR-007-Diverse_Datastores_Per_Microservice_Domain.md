# ADR 7: Adopt Diverse Datastores per Microservice Domain

**Status:** Accepted  
**Date:** 2025-10-08  
**Decision Makers:** @TopSwagCode

## Context
From the start, the project aimed to illustrate how each **microservice** can operate independently — including owning its own data storage.  
Rather than enforcing a single database technology, the goal was to highlight how different domains can choose the datastore that best fits their functional and technical needs.  
This approach emphasizes **domain autonomy**, **data encapsulation**, and the freedom for teams to evolve their own persistence strategies.

## Decision
We decided that **each microservice or domain will maintain its own datastore**, and that the stack should be intentionally diverse to demonstrate real-world flexibility:  
- **Task Service** → PostgreSQL (popular, reliable relational database).  
- **Auth Service** → PostgreSQL (familiar and well-supported for authentication data).  
- **Analytics Service** → MongoDB (document-based model suitable for flexible analytical data).  
- **Event System** → Kafka (widely used distributed log for durable event streaming).  

Kafka was chosen specifically to highlight long-term event storage and replay capabilities, which makes it a good educational choice compared to transient message brokers.

## Consequences

- ✅ Demonstrates domain-driven design principles with true data ownership per service.  
- ✅ Encourages experimentation with different database paradigms.  
- ✅ Kafka allows replaying and analyzing historical events for debugging or analytics.  
- ❌ Increases operational complexity with multiple database technologies to manage.  
- ❌ Harder to ensure global consistency and cross-service queries.

## Alternatives Considered

- **Single Shared Database**: Rejected because it violates service independence and creates coupling.  
- **Uniform Datastore (e.g., all Postgres)**: Rejected to maintain diversity and better showcase polyglot persistence.  
- **RabbitMQ / NATS for Events**: Rejected because these systems delete messages after consumption, while **Kafka** retains them longer and supports replay — aligning with the educational goals of this architecture.
