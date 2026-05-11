# Recommended GitHub Repository Topics

Adding repository topics helps GitHub understand each project and makes the automated profile cards show stronger tags.

## Suggested topics

| Repository | Topics to add |
|---|---|
| `LibraCore` | `java`, `spring-boot`, `spring-security`, `jwt`, `rest-api`, `mysql`, `docker`, `backend` |
| `Knowledge-Studio` | `rag`, `llm`, `knowledge-base`, `python`, `backend`, `api`, `automation` |
| `TaskLang` | `compiler`, `parser`, `bison`, `flex`, `c`, `language-design`, `cli` |
| `Distributed_Systems_Group_30` | `distributed-systems`, `microservices`, `messaging`, `java`, `docker`, `fault-tolerance` |

## Fast method using GitHub CLI

Run these commands after logging in with `gh auth login`:

```bash
gh repo edit Sachith-02/LibraCore --add-topic java --add-topic spring-boot --add-topic spring-security --add-topic jwt --add-topic rest-api --add-topic mysql --add-topic docker --add-topic backend

gh repo edit Sachith-02/Knowledge-Studio --add-topic rag --add-topic llm --add-topic knowledge-base --add-topic python --add-topic backend --add-topic api --add-topic automation

gh repo edit Sachith-02/TaskLang --add-topic compiler --add-topic parser --add-topic bison --add-topic flex --add-topic c --add-topic language-design --add-topic cli

gh repo edit Sachith-02/Distributed_Systems_Group_30 --add-topic distributed-systems --add-topic microservices --add-topic messaging --add-topic java --add-topic docker --add-topic fault-tolerance
```

## Manual method

1. Open the repository on GitHub.
2. Click the gear icon near the **About** section.
3. Add the topics.
4. Save changes.
5. Run the profile automation workflow again.
