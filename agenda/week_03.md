# Week 3: Better Prompts & Structured Output

**Month:** 1 (First Steps) | **Duration:** 6-8 hours

---

## Overview

Your chatbot works, but it returns free-form text. This week you'll learn to make it return **structured data** (JSON) reliably. This is essential for building real applications where you need predictable outputs.

---

## Learning Objectives

By the end of this week, you will:
- Understand prompt engineering patterns (zero-shot, few-shot, chain-of-thought)
- Get the AI to return valid JSON consistently
- Use Pydantic to validate AI outputs
- Build retry logic for when outputs fail validation
- Handle hallucinations and reduce them

---

## Theory (2 hours)

### 1. Why Prompts Matter (30 min)

**Prompting is programming.** The better your prompt, the better the output.

**Bad prompt:**
```
Tell me about this product
```

**Good prompt:**
```
You are a product analyst. Analyze this product and return:
- Name
- Category
- Price range (low/medium/high)
- Key features (list of 3-5)

Product description: {description}

Return JSON format only.
```

### 2. Prompting Techniques (45 min)

| Technique | Description | Example |
|-----------|-------------|---------|
| **Zero-shot** | Just describe what you want | "Summarize this text in 3 sentences" |
| **Few-shot** | Give examples | "Input: X → Output: Y. Now do: Z" |
| **Chain-of-thought** | Ask for reasoning | "Think step by step, then give final answer" |
| **Role prompting** | Assign expertise | "You are an expert lawyer..." |

**Few-shot example:**
```
Extract the sentiment from these reviews:

Review: "I love this product!" → Sentiment: positive
Review: "Terrible, waste of money" → Sentiment: negative  
Review: "It's okay, nothing special" → Sentiment: neutral

Review: "Best purchase ever!" → Sentiment:
```

### 3. Structured Output (30 min)

**Why JSON?**
- Predictable format for code to process
- Can be validated
- Easy to integrate with databases/APIs

**Methods to get JSON:**

| Method | Reliability | How |
|--------|-------------|-----|
| **Ask nicely** | 70% | "Return JSON..." |
| **JSON mode** | 95% | `response_format={"type": "json_object"}` |
| **Structured outputs** | 99% | Provide Pydantic schema |

### 4. Validation with Pydantic (15 min)

```python
from pydantic import BaseModel

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool
```

**Pydantic validates:**
- Required fields are present
- Types are correct
- Values are within constraints

### 5. Human-in-the-Loop Patterns (30 min)

**Why human-in-the-loop?**
AI isn't perfect. For high-stakes decisions, you need human approval:

```
User Request → [AI Processes] → [Human Reviews] → [Action Executed]
                                      ↓
                              Approve / Reject / Edit
```

**When to use:**
| Scenario | Why Human Needed |
|----------|------------------|
| Sending emails | AI might write inappropriate content |
| Financial transactions | Errors could be costly |
| Customer responses | Brand reputation at stake |
| Content publishing | Legal/compliance requirements |
| Data deletion | Irreversible action |

**Confidence-based escalation:**
```python
if response.confidence > 0.9:
    execute_automatically()
elif response.confidence > 0.7:
    execute_with_notification()  # Human can review after
else:
    require_human_approval()     # Wait for human
```

**Design patterns:**
1. **Approval queue** — AI drafts, human approves before sending
2. **Suggestion mode** — AI suggests, human decides
3. **Confidence thresholds** — Auto-approve high confidence, escalate low
4. **Audit trail** — Log all AI decisions for human review

---

## Hands-On Practice (4-6 hours)

### Task 1: Basic JSON Responses (45 min)

```python
# json_basics.py
from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

def analyze_product(description: str) -> dict:
    """Get structured analysis of a product."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Analyze the product and return JSON with:
{
    "name": "product name",
    "category": "category",
    "sentiment": "positive/negative/neutral",
    "key_features": ["feature1", "feature2", "feature3"]
}
Return ONLY valid JSON, no other text."""
            },
            {"role": "user", "content": description}
        ],
        response_format={"type": "json_object"}  # Enforce JSON
    )
    
    return json.loads(response.choices[0].message.content)

# Test
product = """
The new iPhone 15 Pro has an amazing camera system with 48MP resolution.
The titanium design makes it lighter than ever. Great battery life too!
"""

result = analyze_product(product)
print(json.dumps(result, indent=2))
```

### Task 2: Pydantic Validation (60 min)

```python
# pydantic_validation.py
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

# Define your data structure
class ProductAnalysis(BaseModel):
    name: str = Field(description="Product name")
    category: str = Field(description="Product category")
    price_estimate: Optional[float] = Field(None, description="Estimated price in USD")
    sentiment: str = Field(description="positive, negative, or neutral")
    key_features: List[str] = Field(description="3-5 key features")
    confidence: float = Field(ge=0, le=1, description="Confidence score 0-1")

def analyze_product_validated(description: str) -> ProductAnalysis:
    """Get validated product analysis."""
    
    # Create prompt with schema
    schema = ProductAnalysis.model_json_schema()
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system", 
                "content": f"""Analyze the product. Return valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Return ONLY the JSON object."""
            },
            {"role": "user", "content": description}
        ],
        response_format={"type": "json_object"}
    )
    
    # Parse and validate
    data = json.loads(response.choices[0].message.content)
    return ProductAnalysis(**data)

# Test
product = "The Sony WH-1000XM5 headphones offer industry-leading noise cancellation."
result = analyze_product_validated(product)
print(f"Name: {result.name}")
print(f"Category: {result.category}")
print(f"Sentiment: {result.sentiment}")
print(f"Features: {result.key_features}")
```

### Task 3: Retry on Failure (60 min)

```python
# retry_logic.py
from openai import OpenAI
from pydantic import BaseModel, ValidationError
from typing import List
from dotenv import load_dotenv
import json
import time

load_dotenv()
client = OpenAI()

class EmailExtraction(BaseModel):
    sender: str
    subject: str
    is_urgent: bool
    action_items: List[str]
    sentiment: str  # positive, negative, neutral

def extract_with_retry(email_text: str, max_retries: int = 3) -> EmailExtraction:
    """Extract email data with retry logic."""
    
    last_error = None
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": """Extract data from the email. Return JSON:
{
    "sender": "name or email",
    "subject": "email subject/topic",
    "is_urgent": true or false,
    "action_items": ["item1", "item2"],
    "sentiment": "positive/negative/neutral"
}"""
                    },
                    {"role": "user", "content": email_text}
                ],
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response.choices[0].message.content)
            result = EmailExtraction(**data)
            return result
            
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(0.5)  # Brief pause before retry
    
    raise Exception(f"Failed after {max_retries} attempts: {last_error}")

# Test
email = """
From: boss@company.com
Subject: URGENT: Q4 Report Needed

Hi team,

Please complete the Q4 report by tomorrow. Also schedule a review meeting.
This is top priority!

Thanks,
John
"""

result = extract_with_retry(email)
print(f"Sender: {result.sender}")
print(f"Urgent: {result.is_urgent}")
print(f"Actions: {result.action_items}")
```

### Task 4: Few-Shot Prompting (45 min)

```python
# few_shot.py
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def classify_intent(message: str) -> str:
    """Classify user intent using few-shot prompting."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Classify the user's intent. Examples:

Message: "I want to cancel my subscription"
Intent: cancellation

Message: "How do I reset my password?"
Intent: support

Message: "What plans do you offer?"
Intent: pricing

Message: "Your product is amazing!"
Intent: feedback

Message: "I can't login to my account"
Intent: support

Respond with only the intent category."""
            },
            {"role": "user", "content": message}
        ]
    )
    
    return response.choices[0].message.content.strip().lower()

# Test various messages
messages = [
    "I want a refund",
    "How much does the pro plan cost?",
    "I love using your app!",
    "My payment didn't go through",
    "Please delete my account"
]

for msg in messages:
    intent = classify_intent(msg)
    print(f"'{msg}' → {intent}")
```

### Task 5: Chain-of-Thought (45 min)

```python
# chain_of_thought.py
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class ReasonedAnswer(BaseModel):
    reasoning: str
    answer: str
    confidence: float

def answer_with_reasoning(question: str) -> ReasonedAnswer:
    """Get an answer with step-by-step reasoning."""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Think through the problem step by step before answering.

Return JSON:
{
    "reasoning": "Step 1: ... Step 2: ... Step 3: ...",
    "answer": "Your final answer",
    "confidence": 0.0 to 1.0
}"""
            },
            {"role": "user", "content": question}
        ],
        response_format={"type": "json_object"}
    )
    
    data = json.loads(response.choices[0].message.content)
    return ReasonedAnswer(**data)

# Test
questions = [
    "If a train leaves at 9am going 60mph, and another leaves at 10am going 80mph, when do they meet?",
    "Should I use Python or JavaScript for a machine learning project?",
    "A bat and ball cost $1.10 total. The bat costs $1 more than the ball. How much is the ball?"
]

for q in questions:
    result = answer_with_reasoning(q)
    print(f"\nQ: {q}")
    print(f"Reasoning: {result.reasoning}")
    print(f"Answer: {result.answer}")
    print(f"Confidence: {result.confidence}")
```

### Task 6: Upgrade Your Chatbot (60 min)

Add structured output to your Week 2 chatbot:

```python
# structured_chatbot.py
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class ChatResponse(BaseModel):
    message: str
    mood: str  # helpful, curious, apologetic, enthusiastic
    follow_up_questions: List[str] = []
    topic: str
    confidence: float

class StructuredChatbot:
    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt
        self.messages = []
    
    def chat(self, user_message: str) -> ChatResponse:
        """Get a structured response from the chatbot."""
        
        self.messages.append({"role": "user", "content": user_message})
        
        system = f"""{self.system_prompt}

Always respond with JSON:
{{
    "message": "your response to the user",
    "mood": "helpful/curious/apologetic/enthusiastic",
    "follow_up_questions": ["suggested question 1", "suggested question 2"],
    "topic": "the main topic discussed",
    "confidence": 0.0 to 1.0 (how confident you are)
}}"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system},
                *self.messages
            ],
            response_format={"type": "json_object"}
        )
        
        data = json.loads(response.choices[0].message.content)
        result = ChatResponse(**data)
        
        # Store just the message in history
        self.messages.append({"role": "assistant", "content": result.message})
        
        return result

# Interactive test
if __name__ == "__main__":
    bot = StructuredChatbot("You are a helpful coding assistant.")
    
    print("Structured Chatbot! Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            break
        
        response = bot.chat(user_input)
        
        print(f"AI [{response.mood}]: {response.message}")
        if response.follow_up_questions:
            print(f"   You could ask: {response.follow_up_questions[0]}")
        print()
```

### Task 7: Human-in-the-Loop Approval (60 min)

Build an email assistant that requires human approval before sending:

```python
# human_in_loop.py
from openai import OpenAI
from pydantic import BaseModel
from typing import Literal
from dotenv import load_dotenv
import json

load_dotenv()
client = OpenAI()

class EmailDraft(BaseModel):
    to: str
    subject: str
    body: str
    confidence: float
    risk_level: Literal["low", "medium", "high"]
    needs_review: bool

class ApprovalResult(BaseModel):
    approved: bool
    edited_body: str | None = None
    reason: str | None = None

def draft_email(request: str) -> EmailDraft:
    """AI drafts an email based on user request."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """Draft a professional email based on the request.
Return JSON:
{
    "to": "recipient email",
    "subject": "email subject",
    "body": "email body",
    "confidence": 0.0-1.0,
    "risk_level": "low/medium/high",
    "needs_review": true if sensitive content or low confidence
}"""
            },
            {"role": "user", "content": request}
        ],
        response_format={"type": "json_object"}
    )
    return EmailDraft(**json.loads(response.choices[0].message.content))

def get_human_approval(draft: EmailDraft) -> ApprovalResult:
    """Present draft to human for approval."""
    print("\n" + "="*50)
    print("📧 EMAIL DRAFT FOR APPROVAL")
    print("="*50)
    print(f"To: {draft.to}")
    print(f"Subject: {draft.subject}")
    print(f"Risk Level: {draft.risk_level}")
    print(f"AI Confidence: {draft.confidence:.0%}")
    print("-"*50)
    print(draft.body)
    print("-"*50)
    
    choice = input("\n[A]pprove / [E]dit / [R]eject: ").strip().lower()
    
    if choice == 'a':
        return ApprovalResult(approved=True)
    elif choice == 'e':
        edited = input("Enter corrected body: ")
        return ApprovalResult(approved=True, edited_body=edited)
    else:
        reason = input("Rejection reason: ")
        return ApprovalResult(approved=False, reason=reason)

def send_email(draft: EmailDraft):
    """Simulate sending email."""
    print(f"\n✅ Email sent to {draft.to}!")

def email_with_approval(request: str):
    """Complete flow: draft → approval → send."""
    draft = draft_email(request)
    
    # Auto-approve low risk + high confidence
    if draft.risk_level == "low" and draft.confidence > 0.9 and not draft.needs_review:
        print("Auto-approved (low risk, high confidence)")
        send_email(draft)
        return
    
    # Otherwise, get human approval
    approval = get_human_approval(draft)
    
    if approval.approved:
        if approval.edited_body:
            draft.body = approval.edited_body
        send_email(draft)
    else:
        print(f"❌ Email rejected: {approval.reason}")

# Test
if __name__ == "__main__":
    email_with_approval("Write an email to john@company.com apologizing for the delayed shipment")
```

---

## Knowledge Checklist

- [ ] I understand zero-shot, few-shot, and chain-of-thought prompting
- [ ] I can get JSON responses using `response_format`
- [ ] I can validate AI outputs with Pydantic
- [ ] I can build retry logic for failed validations
- [ ] I can use few-shot examples to improve accuracy
- [ ] I upgraded my chatbot to return structured data
- [ ] I understand when and how to implement human-in-the-loop patterns
- [ ] I can build confidence-based approval workflows

---

## Deliverables

1. `json_basics.py` — Basic JSON extraction
2. `pydantic_validation.py` — Validated extraction
3. `retry_logic.py` — Retry on validation failure
4. `few_shot.py` — Intent classifier with examples
5. `structured_chatbot.py` — Chatbot with structured responses
6. `human_in_loop.py` — Email assistant with approval workflow

---

## What's Next?

Next week, you'll connect your chatbot to your own documents! This is called RAG (Retrieval-Augmented Generation) — the most important technique in AI engineering.

---

## Resources

- [OpenAI JSON Mode](https://platform.openai.com/docs/guides/structured-outputs)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
