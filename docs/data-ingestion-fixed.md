<div align="center">

# Data Ingestion
```mermaid
flowchart LR
    A[Reddit Posts] -->|PRAW| B[Scraper]
    B -->|Process| C[Comments]
    C -->|Embed| D[Vector DB]
    D -->|Index| E[SearchAPI]
```

</div>
