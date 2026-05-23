# Stack-detection cheatsheet

Fingerprint the target project's language, framework, AI/ML stack, runtime, and data layer. Each row is a signal; combine signals to resolve the stack.

## Language signals

| Language | Primary signal | Secondary signals |
|---|---|---|
| Python | `pyproject.toml` / `requirements*.txt` / `setup.py` / `Pipfile` / `uv.lock` / `poetry.lock` | `.python-version`, `*.py` file dominance |
| JavaScript | `package.json` with no `typescript` dep | `*.js` files, `.babelrc` |
| TypeScript | `tsconfig.json`, `typescript` dep in package.json | `*.ts` / `*.tsx` files |
| Go | `go.mod` | `*.go` files |
| Rust | `Cargo.toml` | `*.rs` files, `Cargo.lock` |
| Ruby | `Gemfile` | `*.rb`, `.ruby-version` |
| Java | `pom.xml` / `build.gradle` | `*.java` |
| HCL/Terraform | `*.tf`, `*.tfvars`, `.terraform.lock.hcl` | `provider.tf` |

## Python framework signals

| Framework | Primary signal | Code signal |
|---|---|---|
| FastAPI | `fastapi` in deps + `uvicorn` | `from fastapi import` |
| Flask | `flask` in deps | `from flask import`, `app = Flask(__name__)` |
| Django | `django` in deps, `manage.py`, `settings.py` | `INSTALLED_APPS = [...]` |
| Starlette | `starlette` in deps (often via FastAPI) | `from starlette.` |
| Litestar | `litestar` in deps | `from litestar import` |

## JS/TS framework signals

| Framework | Primary signal | Code signal |
|---|---|---|
| Next.js | `next` in package.json, `next.config.js` | `pages/` or `app/` directory |
| React (standalone) | `react` in deps, no `next` | `import React from 'react'` |
| Express | `express` in deps | `const app = express()` |
| NestJS | `@nestjs/core` in deps | `@Controller()` / `@Injectable()` decorators |
| Svelte / SvelteKit | `svelte` / `@sveltejs/kit` in deps | `*.svelte` files |
| Vue | `vue` in deps | `*.vue` files |

## AI/ML stack signals

| Stack | Primary signal | Code signal |
|---|---|---|
| LangChain | `langchain` / `langchain-core` / `langchain-openai` / `langchain-anthropic` in deps | `from langchain` |
| LlamaIndex | `llama-index` / `llama-index-core` | `from llama_index` |
| OpenAI client | `openai` in deps | `from openai import OpenAI` |
| Anthropic client | `anthropic` in deps | `from anthropic import Anthropic` |
| Cohere client | `cohere` in deps | `import cohere` |
| Vector DB — Chroma | `chromadb` | `import chromadb` |
| Vector DB — Qdrant | `qdrant-client` | `from qdrant_client import` |
| Vector DB — Weaviate | `weaviate-client` | `import weaviate` |
| Vector DB — pgvector | `pgvector` extension + `psycopg` | `CREATE EXTENSION vector` |
| Vector DB — Pinecone | `pinecone-client` | `from pinecone import` |
| HuggingFace | `transformers` / `datasets` / `accelerate` | `from transformers import` |
| PyTorch | `torch` | `import torch` |
| TensorFlow | `tensorflow` | `import tensorflow as tf` |
| RAG indicators | combination of: loader + splitter + retriever + vector DB | `RecursiveCharacterTextSplitter`, `Retriever`, `VectorStore` |

## Data layer signals

| Layer | Primary signal | Code signal |
|---|---|---|
| SQLAlchemy | `sqlalchemy` in deps | `from sqlalchemy import` |
| Django ORM | `django` (covered above) | `models.Model` subclasses |
| Prisma | `@prisma/client` in deps, `schema.prisma` | `import { PrismaClient }` |
| TypeORM | `typeorm` in deps | `@Entity()` decorator |
| Drizzle | `drizzle-orm` in deps | `import { drizzle } from 'drizzle-orm'` |
| Raw `psycopg` / `psycopg2` | dep + import | `psycopg.connect(...)` |
| MongoDB | `pymongo` / `mongoose` | `MongoClient(...)` |
| Redis | `redis` / `ioredis` | `Redis(...)` |

## Runtime / deployment signals

| Runtime | Primary signal |
|---|---|
| Dockerfile / Containerfile | file presence at repo root |
| docker-compose | `docker-compose.yml` / `compose.yaml` |
| Kubernetes | `*.yaml` with `kind: Deployment` / `kind: Service` |
| Serverless Framework | `serverless.yml` / `serverless.ts` |
| AWS SAM | `template.yaml` with `Transform: AWS::Serverless-2016-10-31` |
| Vercel | `vercel.json` |
| Cloudflare Workers | `wrangler.toml` |
| Fly.io | `fly.toml` |

## Output: stack manifest

After detection, emit a top-of-report manifest:

```
Stack manifest:
- Languages: <list, dominant first>
- Frameworks: <list>
- AI/ML stack: <list, or "none detected">
- Data layer: <list>
- Runtime: <list, or "none detected">
- Test framework: <pytest / jest / vitest / mocha / ... or "none detected">
```

The user can correct any line via `stack_overrides`. Print a one-line reminder: *"If any line is wrong, re-run with `stack_overrides: {...}`."*

## Ambiguity handling

- **Multiple frameworks in one repo** — common in monorepos. Detect per top-level directory (e.g., `backend/` is FastAPI, `frontend/` is Next.js) and apply rules per-directory.
- **Library vs application** — a `langchain` dep does not mean LangChain is *used*. Confirm by greppable imports across the codebase.
- **Transitive imports** — `langchain-core` may be present transitively via `langchain-community`. Treat top-level pyproject/requirements declarations as the authoritative stack list; transitive deps inform but do not drive applicability.
