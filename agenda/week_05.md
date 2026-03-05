# Week 5: Evaluations & Quality Metrics

**Month:** 2 (Quality & Safety) | **Duration:** 6-8 hours

---

## Overview

Your RAG system generates answers, but **how do you know if they're any good?** This week you'll learn to measure AI quality systematically — a critical skill for production AI systems.

---

## Learning Objectives

By the end of this week, you will:
- Understand why evaluation matters
- Build test datasets for your AI
- Implement automatic quality metrics
- Use LLM-as-a-judge evaluation
- Set up regression testing for AI

---

## Model Options

| Feature | OpenAI (Paid) | Ollama (Free/Local) |
|---------|--------------|---------------------|
| System under test | `gpt-4o-mini` | `llama3.1:8b` |
| LLM-as-judge | `gpt-4o-mini` | `qwq:32b` (strong reasoning) or `llama3.1:8b` (faster) |

**Quick start with Ollama:**
```bash
ollama pull llama3.1:8b   # system under test
ollama pull qwq:32b       # judge model (requires ~20GB RAM); use llama3.1:8b as fallback
```

```python
from scripts.model_config import get_client, CHAT_MODEL, REASON_MODEL
# REASON_MODEL defaults to qwq:32b (Ollama) / gpt-4o-mini (OpenAI)
```

> Tip: For LLM-as-judge, use a *different* (ideally stronger) model than the one being evaluated to avoid bias.

---

## Theory (2 hours)

### 1. Why Evaluate AI? (30 min)

**The problem:** AI outputs are non-deterministic. The same question can give different answers.

**Without evaluation:**
- "It seems to work" → ships broken AI
- Can't measure improvements
- No way to catch regressions

**With evaluation:**
- Quantified quality scores
- Know when changes help/hurt
- Confident deployments

### 2. Evaluation Types (30 min)

| Type | What It Measures | How |
|------|------------------|-----|
| **Retrieval** | Did we find the right documents? | Precision, Recall |
| **Generation** | Is the answer good? | Faithfulness, Relevance |
| **End-to-End** | Does the whole system work? | Answer correctness |

### 3. Key Metrics (30 min)

**Retrieval Metrics:**
```
Precision = relevant retrieved / total retrieved
Recall = relevant retrieved / total relevant

Example: Query finds 5 docs, 3 are relevant, 2 relevant docs exist
- Precision = 3/5 = 60%
- Recall = 3/2... wait, can't find more than exist!
```

**Generation Metrics:**
- **Faithfulness**: Does the answer match the context? (no hallucination)
- **Relevance**: Does the answer address the question?
- **Completeness**: Did we answer the full question?

### 4. LLM-as-a-Judge (30 min)

**Use one LLM to evaluate another:**
```python
prompt = f"""
Rate this answer on a scale of 1-5:

Question: {question}
Context: {context}
Answer: {answer}

Criteria:
- Factual accuracy (matches context)
- Completeness (answers the question fully)
- Relevance (no off-topic information)

Return JSON: {{"score": 1-5, "reason": "..."}}
"""
```

**Pros:** Scalable, nuanced evaluation
**Cons:** Can be biased, costs money

### 5. Ground-Truth Curation (30 min)

**Golden datasets** are your source of truth for evaluation.

**Creating ground-truth data:**
| Method | Pros | Cons |
|--------|------|------|
| **Expert labeling** | High quality | Expensive, slow |
| **Crowdsourcing** | Scalable | Quality varies |
| **LLM-assisted** | Fast | Needs verification |
| **Production sampling** | Realistic | Delayed feedback |

**Best practices:**
1. **Diverse questions** — Cover edge cases, not just happy paths
2. **Multiple correct answers** — "20 days" vs "Twenty days" both valid
3. **Annotator guidelines** — Clear criteria for labelers
4. **Inter-rater agreement** — Multiple people label same items
5. **Regular updates** — Refresh as product changes

```python
# Labeling workflow example
golden_test = {
    "question": "How many vacation days?",
    "acceptable_answers": [
        "20 days",
        "Twenty days",
        "20 PTO days per year"
    ],
    "required_docs": ["vacation_policy.txt"],
    "difficulty": "easy",
    "labeled_by": ["expert_1", "expert_2"],
    "created_date": "2025-01-15"
}
```

### 6. CI/CD Integration for Prompt Testing (30 min)

**Run evaluations automatically on every change:**

```yaml
# .github/workflows/eval.yml
name: AI Evaluation

on:
  push:
    paths:
      - 'prompts/**'
      - 'src/rag/**'

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run evaluations
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: python run_evaluation.py
      
      - name: Check for regression
        run: python check_regression.py --threshold 0.80
```

**Key metrics to gate deployments:**
- Overall score > 0.80 (or your threshold)
- No individual metric below 0.60
- No regression > 5% from baseline

---

## Hands-On Practice (4-6 hours)

### Task 1: Create a Test Dataset (45 min)

```python
# test_dataset.py
import json

# Create test questions with expected answers
test_cases = [
    {
        "id": 1,
        "question": "How many vacation days do employees get after 2 years?",
        "expected_answer": "20 days",
        "relevant_doc": "vacation_policy.txt"
    },
    {
        "id": 2,
        "question": "Can I work from home on Wednesday?",
        "expected_answer": "No, Wednesday is a required office day",
        "relevant_doc": "remote_work.txt"
    },
    {
        "id": 3,
        "question": "What's the 401k match?",
        "expected_answer": "4% company match",
        "relevant_doc": "benefits.txt"
    },
    {
        "id": 4,
        "question": "How much is the home office equipment allowance?",
        "expected_answer": "$500",
        "relevant_doc": "remote_work.txt"
    },
    {
        "id": 5,
        "question": "When should I request vacation?",
        "expected_answer": "At least 2 weeks in advance",
        "relevant_doc": "vacation_policy.txt"
    }
]

# Save
with open("test_data.json", "w") as f:
    json.dump(test_cases, f, indent=2)

print(f"Created {len(test_cases)} test cases")
```

### Task 2: Simple Correctness Check (45 min)

```python
# simple_eval.py
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
import json

load_dotenv()
client = OpenAI()

class CorrectnessScore(BaseModel):
    score: int  # 1-5
    reason: str
    matches_expected: bool

def check_correctness(question: str, answer: str, expected: str) -> CorrectnessScore:
    """Check if answer matches expected answer."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You evaluate AI answers."},
            {"role": "user", "content": f"""
Compare the answer to the expected answer.

Question: {question}
Expected Answer: {expected}
Actual Answer: {answer}

Return JSON:
{{
    "score": 1-5 (1=completely wrong, 5=perfect match),
    "reason": "brief explanation",
    "matches_expected": true/false
}}"""}
        ],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    return CorrectnessScore(**data)

# Test
if __name__ == "__main__":
    result = check_correctness(
        question="How many vacation days after 2 years?",
        answer="Employees receive 20 days of paid time off after working for 2 years.",
        expected="20 days"
    )
    
    print(f"Score: {result.score}/5")
    print(f"Matches: {result.matches_expected}")
    print(f"Reason: {result.reason}")
```

### Task 3: Faithfulness Evaluation (60 min)

```python
# faithfulness_eval.py
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List
import json

load_dotenv()
client = OpenAI()

class FaithfulnessResult(BaseModel):
    score: float  # 0-1
    claims: List[str]
    supported_claims: List[str]
    unsupported_claims: List[str]

def evaluate_faithfulness(context: str, answer: str) -> FaithfulnessResult:
    """Check if all claims in the answer are supported by context."""
    
    # Step 1: Extract claims from answer
    claims_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Extract factual claims from text."},
            {"role": "user", "content": f"""
Extract all factual claims from this answer:

"{answer}"

Return JSON: {{"claims": ["claim 1", "claim 2", ...]}}"""}
        ],
        response_format={"type": "json_object"}
    )
    
    claims_data = json.loads(claims_response.choices[0].message.content)
    claims = claims_data.get("claims", [])
    
    if not claims:
        return FaithfulnessResult(
            score=1.0, claims=[], supported_claims=[], unsupported_claims=[]
        )
    
    # Step 2: Check each claim against context
    supported = []
    unsupported = []
    
    for claim in claims:
        verify_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": f"""
Is this claim supported by the context?

Context: {context}

Claim: {claim}

Return JSON: {{"supported": true/false}}"""}
            ],
            response_format={"type": "json_object"}
        )
        
        verify_data = json.loads(verify_response.choices[0].message.content)
        
        if verify_data.get("supported"):
            supported.append(claim)
        else:
            unsupported.append(claim)
    
    score = len(supported) / len(claims) if claims else 1.0
    
    return FaithfulnessResult(
        score=score,
        claims=claims,
        supported_claims=supported,
        unsupported_claims=unsupported
    )

# Test
if __name__ == "__main__":
    context = """
    Employees receive 20 days of paid time off after 2 years of employment.
    Vacation must be requested 2 weeks in advance through the HR portal.
    """
    
    # Good answer (faithful)
    good_answer = "After 2 years, you get 20 vacation days. Request them 2 weeks ahead."
    
    # Bad answer (has hallucination)
    bad_answer = "You get 20 vacation days, and you can also carry over up to 30 days."
    
    print("=== Good Answer ===")
    result = evaluate_faithfulness(context, good_answer)
    print(f"Score: {result.score:.2f}")
    print(f"Supported: {result.supported_claims}")
    print(f"Unsupported: {result.unsupported_claims}")
    
    print("\n=== Bad Answer ===")
    result = evaluate_faithfulness(context, bad_answer)
    print(f"Score: {result.score:.2f}")
    print(f"Supported: {result.supported_claims}")
    print(f"Unsupported: {result.unsupported_claims}")
```

### Task 4: RAG Evaluation Pipeline (60 min)

```python
# rag_evaluator.py
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
import json

load_dotenv()
client = OpenAI()

@dataclass
class EvalResult:
    question: str
    answer: str
    retrieval_score: float  # Did we find right docs?
    faithfulness_score: float  # Answer matches context?
    correctness_score: float  # Answer is correct?
    overall_score: float

def evaluate_rag_response(
    question: str,
    answer: str,
    context: str,
    expected_answer: str,
    expected_doc: str,
    retrieved_docs: List[str]
) -> EvalResult:
    """Comprehensive RAG evaluation."""
    
    # 1. Retrieval score: Did we find the expected document?
    retrieval_score = 1.0 if expected_doc in retrieved_docs else 0.0
    
    # 2. Faithfulness: Is answer grounded in context?
    faith_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"""
Score how well the answer is supported by the context (0-1):

Context: {context}
Answer: {answer}

Return JSON: {{"score": 0.0-1.0, "reason": "..."}}"""}
        ],
        response_format={"type": "json_object"}
    )
    faithfulness_score = json.loads(faith_response.choices[0].message.content)["score"]
    
    # 3. Correctness: Does answer match expected?
    correct_response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"""
Score how well the answer matches the expected answer (0-1):

Question: {question}
Expected: {expected_answer}
Actual: {answer}

Return JSON: {{"score": 0.0-1.0}}"""}
        ],
        response_format={"type": "json_object"}
    )
    correctness_score = json.loads(correct_response.choices[0].message.content)["score"]
    
    # Overall score (weighted average)
    overall = (retrieval_score * 0.3 + faithfulness_score * 0.4 + correctness_score * 0.3)
    
    return EvalResult(
        question=question,
        answer=answer,
        retrieval_score=retrieval_score,
        faithfulness_score=faithfulness_score,
        correctness_score=correctness_score,
        overall_score=overall
    )

# Test
if __name__ == "__main__":
    result = evaluate_rag_response(
        question="How many vacation days after 2 years?",
        answer="After working for 2 years, employees receive 20 days of PTO.",
        context="Employees with 2-5 years tenure receive 20 days per year.",
        expected_answer="20 days",
        expected_doc="vacation_policy.txt",
        retrieved_docs=["vacation_policy.txt", "benefits.txt"]
    )
    
    print(f"Question: {result.question}")
    print(f"Answer: {result.answer}")
    print(f"\nScores:")
    print(f"  Retrieval:    {result.retrieval_score:.2f}")
    print(f"  Faithfulness: {result.faithfulness_score:.2f}")
    print(f"  Correctness:  {result.correctness_score:.2f}")
    print(f"  Overall:      {result.overall_score:.2f}")
```

### Task 5: Run Full Evaluation Suite (45 min)

```python
# run_evaluation.py
from rag_evaluator import evaluate_rag_response, EvalResult
from typing import List
import json

def run_evaluation_suite(rag_system, test_file: str = "test_data.json") -> List[EvalResult]:
    """Run all test cases through the RAG system and evaluate."""
    
    # Load test cases
    with open(test_file) as f:
        test_cases = json.load(f)
    
    results = []
    
    for test in test_cases:
        print(f"Testing: {test['question'][:50]}...")
        
        # Get RAG response (mock for now)
        # response = rag_system.ask(test['question'])
        
        # Mock response for demo
        mock_answer = f"Based on the {test['relevant_doc']}, {test['expected_answer']}."
        mock_context = f"Document content about {test['expected_answer']}."
        mock_docs = [test['relevant_doc']]
        
        result = evaluate_rag_response(
            question=test['question'],
            answer=mock_answer,
            context=mock_context,
            expected_answer=test['expected_answer'],
            expected_doc=test['relevant_doc'],
            retrieved_docs=mock_docs
        )
        
        results.append(result)
    
    return results

def print_summary(results: List[EvalResult]):
    """Print evaluation summary."""
    
    if not results:
        print("No results")
        return
    
    avg_retrieval = sum(r.retrieval_score for r in results) / len(results)
    avg_faith = sum(r.faithfulness_score for r in results) / len(results)
    avg_correct = sum(r.correctness_score for r in results) / len(results)
    avg_overall = sum(r.overall_score for r in results) / len(results)
    
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Total test cases: {len(results)}")
    print(f"\nAverage Scores:")
    print(f"  Retrieval:    {avg_retrieval:.2%}")
    print(f"  Faithfulness: {avg_faith:.2%}")
    print(f"  Correctness:  {avg_correct:.2%}")
    print(f"  Overall:      {avg_overall:.2%}")
    
    # Find failures
    failures = [r for r in results if r.overall_score < 0.7]
    if failures:
        print(f"\n⚠️  {len(failures)} test(s) below 70%:")
        for r in failures:
            print(f"  - {r.question[:50]}... ({r.overall_score:.2%})")

# Run
if __name__ == "__main__":
    # Create test data first
    exec(open("test_dataset.py").read())
    
    results = run_evaluation_suite(None)
    print_summary(results)
```

### Task 6: Regression Testing (30 min)

```python
# regression_test.py
import json
from datetime import datetime
from pathlib import Path

class RegressionTracker:
    """Track evaluation results over time."""
    
    def __init__(self, results_file: str = "eval_history.json"):
        self.results_file = Path(results_file)
        self.history = self._load_history()
    
    def _load_history(self) -> list:
        if self.results_file.exists():
            return json.loads(self.results_file.read_text())
        return []
    
    def save_result(self, scores: dict, version: str = None):
        """Save evaluation result."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": version or "unknown",
            "scores": scores
        }
        
        self.history.append(result)
        self.results_file.write_text(json.dumps(self.history, indent=2))
        
        # Check for regression
        if len(self.history) > 1:
            prev = self.history[-2]["scores"]
            curr = scores
            
            for metric, value in curr.items():
                if metric in prev and value < prev[metric] - 0.05:
                    print(f"⚠️  REGRESSION: {metric} dropped from {prev[metric]:.2%} to {value:.2%}")
    
    def show_history(self):
        """Print history."""
        print("\nEvaluation History:")
        for result in self.history[-5:]:
            print(f"  {result['timestamp']}: {result['scores'].get('overall', 'N/A'):.2%}")

# Usage
if __name__ == "__main__":
    tracker = RegressionTracker()
    
    # Save a result
    tracker.save_result({
        "retrieval": 0.85,
        "faithfulness": 0.90,
        "correctness": 0.88,
        "overall": 0.88
    }, version="v1.0")
    
    tracker.show_history()
```

---

## 🎯 Optional Challenges

*You can't improve what you don't measure. Master evaluation here.*

### Challenge 1: Build a Human Evaluation Interface
Create a simple UI (CLI or web) for human evaluation:
```python
# Show question, expected answer, actual answer
# Collect human ratings (1-5) for:
# - Correctness
# - Helpfulness  
# - Fluency
# Compare human vs LLM-as-judge scores
```

### Challenge 2: Adversarial Test Set
Create intentionally difficult test cases:
- Questions with no answer in documents
- Questions requiring synthesis across documents
- Misleading questions (trick questions)
- Very long context requirements

### Challenge 3: Regression Detection System
Build automated regression detection:
```python
def detect_regression(new_scores, baseline_scores, threshold=0.05):
    # Return list of metrics that dropped significantly
    # Integration: Block PR if regression detected
```

### Challenge 4: Evaluate Across Models
Test the same prompts across different models:
```python
models = ["gpt-4o-mini", "gpt-4o", "claude-sonnet"]
for model in models:
    scores = evaluate_rag(model, test_cases)
    # Compare: Which model performs best?
    # Cost vs quality tradeoff analysis
```

### Challenge 5: Continuous Evaluation Pipeline
Set up automated weekly evaluation:
1. Run evaluation suite every Sunday
2. Compare to last week's baseline
3. Generate report with charts
4. Send Slack notification with summary
5. Archive results to database

---

## Knowledge Checklist

- [ ] I understand why AI evaluation is essential
- [ ] I can create test datasets for RAG
- [ ] I can implement LLM-as-a-judge evaluation
- [ ] I understand faithfulness vs correctness
- [ ] I can track evaluations over time
- [ ] I can detect regressions
- [ ] I understand ground-truth curation best practices
- [ ] I can integrate evaluations into CI/CD pipelines

---

## Deliverables

1. `test_dataset.py` — Create test cases
2. `simple_eval.py` — Basic correctness check
3. `faithfulness_eval.py` — Check for hallucinations
4. `rag_evaluator.py` — Full evaluation pipeline
5. `run_evaluation.py` — Run evaluation suite
6. `regression_test.py` — Track changes over time

---

## What's Next?

Next week: **Security & Guardrails** + your first portfolio project checkpoint!

---

## Resources

- [RAGAS Framework](https://docs.ragas.io/)
- [LangSmith Evaluation](https://docs.smith.langchain.com/)
- [Evaluating LLM Applications](https://www.anthropic.com/news/evaluating-ai-systems)
