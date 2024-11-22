```mermaid
---
config:
  theme: dark
  layout: fixed
title: Assignment Crawling Sequence Diagram
---

sequenceDiagram
    participant LoginWorker
    participant Cookie
    loop Every 3 hours
        LoginWorker -) Cookie: Fetch cookie
        Cookie -) Cookie: Update cookie
    end

    participant AssignmentWorker
    participant Assignment

    loop Every 1 minute
        AssignmentWorker ->> Cookie: Get cookie
        Cookie -->> AssignmentWorker: return cookie

        AssignmentWorker ->> Assignment: Get assignment
        Assignment -->> AssignmentWorker: return assignment

        AssignmentWorker -) Assignment: Fetch updates
        Assignment -) Assignment: Update Assignments
    end
```
