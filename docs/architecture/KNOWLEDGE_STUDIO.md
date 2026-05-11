# Knowledge Studio Architecture

Knowledge Studio can be presented as an AI-assisted knowledge or RAG-style backend project. This diagram shows ingestion, indexing, retrieval, and answer generation as separate responsibilities.

```mermaid
flowchart TD
    User[User / Frontend] --> API[Backend API]
    API --> Upload[Document Upload Endpoint]
    Upload --> Parser[Document Parser]
    Parser --> Chunker[Text Chunking]
    Chunker --> Embedder[Embedding Generator]
    Embedder --> VectorDB[(Vector Store)]
    API --> Query[Question Endpoint]
    Query --> Retriever[Semantic Retriever]
    Retriever --> VectorDB
    Retriever --> Context[Relevant Context Builder]
    Context --> LLM[LLM / Answer Generator]
    LLM --> Response[Grounded Response]
    Response --> User
```

## Data pipeline

```mermaid
sequenceDiagram
    participant U as User
    participant API as API
    participant P as Parser
    participant V as Vector Store
    participant L as LLM

    U->>API: Upload document
    API->>P: Extract and clean text
    P->>V: Store chunks + embeddings
    U->>API: Ask question
    API->>V: Search similar chunks
    V-->>API: Relevant context
    API->>L: Prompt with context
    L-->>API: Answer
    API-->>U: Response with source context
```

## README checklist for this repository

- Explain supported file types.
- Show the ingestion pipeline.
- Add examples of prompts/questions.
- Document limitations, privacy, and token cost.
- Add CI badge and latest release badge.
