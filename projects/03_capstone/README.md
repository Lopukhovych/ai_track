# Portfolio Project #3: Capstone

**Weeks 13-16 Final Project**

Combine everything you've learned into a production-ready AI application.

---

## Choose Your Project

Pick one or combine elements:

### Option A: Enterprise RAG Assistant
- Multi-document RAG with citations
- Tool calling for calculations/lookups
- Admin dashboard for document management
- Evaluation suite
- Docker deployment

### Option B: Autonomous Agent System
- Multi-agent collaboration
- Complex task decomposition
- External API integrations
- State persistence
- Observability & logging

### Option C: Custom Domain Assistant
- Specialized for your industry/interest
- Fine-tuned behavior (prompts or model)
- Production API with rate limiting
- User authentication
- Cost tracking

---

## Minimum Requirements

### All Projects Must Have:

- [ ] **Core AI functionality** - LLM integration that solves a real problem
- [ ] **Production quality** - Error handling, retries, rate limiting
- [ ] **Security** - Input validation, injection prevention
- [ ] **Evaluation** - Defined metrics and test suite
- [ ] **Documentation** - README, API docs, architecture diagram
- [ ] **Deployment** - Docker or cloud deployment ready

### Bonus Points:
- [ ] Multi-modal (vision, audio)
- [ ] Fine-tuned model
- [ ] CI/CD pipeline
- [ ] Cost monitoring
- [ ] User feedback loop

---

## Project Structure

```
03_capstone/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── src/
│   ├── api/              # FastAPI routes
│   ├── core/             # Business logic
│   ├── llm/              # LLM interactions
│   ├── tools/            # Tool definitions
│   └── utils/            # Helpers
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
│   ├── architecture.md
│   └── api.md
└── eval/
    ├── test_cases.json
    └── evaluate.py
```

---

## Deliverables Checklist

### Code
- [ ] Clean, documented code
- [ ] Type hints throughout
- [ ] Unit tests (>70% coverage)
- [ ] Integration tests

### Documentation
- [ ] README with setup instructions
- [ ] Architecture diagram
- [ ] API documentation
- [ ] Cost estimation

### Deployment
- [ ] Dockerfile
- [ ] Environment configuration
- [ ] Health check endpoint

### Presentation
- [ ] 5-minute demo video
- [ ] Slide deck (optional)
- [ ] Live demo capability

---

## Interview Presentation Guide

Structure your capstone presentation:

1. **Problem Statement** (30 sec)
   - What problem does this solve?
   - Who is the user?

2. **Architecture** (1 min)
   - High-level diagram
   - Key components

3. **Demo** (2 min)
   - Happy path walkthrough
   - Show a complex case

4. **Technical Deep Dive** (1 min)
   - Most interesting technical challenge
   - How you solved it

5. **What I Learned** (30 sec)
   - Key takeaways
   - What you'd do differently

---

## Evaluation Rubric

| Criteria | Weight | Description |
|----------|--------|-------------|
| Functionality | 30% | Does it work? Does it solve the problem? |
| Code Quality | 20% | Clean, maintainable, well-structured |
| Production Ready | 20% | Error handling, security, deployment |
| Documentation | 15% | Clear setup, architecture, API docs |
| Innovation | 15% | Creative solutions, above and beyond |
