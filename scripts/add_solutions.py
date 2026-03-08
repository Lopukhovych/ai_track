"""
Script to add hints and solutions to VS Code native notebooks.
Run from the ai-track-v2 directory.

VS Code notebooks use XML format: <VSCode.Cell id="..." language="...">content</VSCode.Cell>
"""
import re
import uuid
from pathlib import Path

def generate_cell_id():
    """Generate a VS Code style cell ID."""
    return f"#VSC-{uuid.uuid4().hex[:8]}"

def add_solution_cells(notebook_path: Path, exercises: list):
    """Add hint and solution cells after exercise cells in VS Code notebooks."""
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has hints (avoid duplicating)
    if '💡 <b>Hint</b>' in content:
        print(f"⏭ Skipping {notebook_path.name} (already has hints)")
        return
    
    for ex in exercises:
        if ex['marker'] not in content:
            continue
            
        # Find the closing tag for the cell containing this marker
        marker_pos = content.find(ex['marker'])
        close_tag_pos = content.find('</VSCode.Cell>', marker_pos)
        
        if close_tag_pos == -1:
            continue
        
        # Insert position is right after </VSCode.Cell>
        insert_pos = close_tag_pos + len('</VSCode.Cell>')
        
        # Build hint and solution cells
        hint_cell = f'''
<VSCode.Cell id="{generate_cell_id()}" language="markdown">
<details>
<summary>💡 <b>Hint</b> (click to expand)</summary>

{ex['hint']}

</details>
</VSCode.Cell>'''
        
        solution_cell = f'''
<VSCode.Cell id="{generate_cell_id()}" language="markdown">
<details>
<summary>✅ <b>Solution</b> (click to expand)</summary>

```python
{ex['solution']}
```

</details>
</VSCode.Cell>'''
        
        # Insert the new cells
        content = content[:insert_pos] + hint_cell + solution_cell + content[insert_pos:]
    
    with open(notebook_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {notebook_path.name}")

# Week 1 exercises
week1_exercises = [
    {
        'marker': '# Exercise 1: Create a translator',
        'hint': '''The system prompt tells the AI what role to play. For translation:
1. Tell it to act as a translator
2. Specify the target language (Spanish)
3. Tell it to only output the translation''',
        'solution': '''response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "You are a translator. Translate to Spanish. Only output the translation."},
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
print(response.choices[0].message.content)
# Output: Hola, ¿cómo estás?'''
    },
    {
        'marker': '# Exercise 2: Create a code explainer',
        'hint': '''This one is already mostly complete! Try variations:
- Change to "Explain like I am 5"
- Add "Use analogies" to the prompt
- Ask for "step by step" explanation''',
        'solution': '''# ELI5 version - great for beginners
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system", "content": "Explain code like I am 5. Use simple analogies."},
        {"role": "user", "content": f"What does this code do?\\n{code}"}
    ]
)
print(response.choices[0].message.content)'''
    }
]

# Week 2 exercises
week2_exercises = [
    {
        'marker': '# Exercise 1: Create a study buddy',
        'hint': '''A study buddy chatbot should:
1. Have a friendly, encouraging persona
2. Remember the topic being studied
3. Ask follow-up questions to test understanding''',
        'solution': '''class StudyBuddy(Chatbot):
    def __init__(self):
        super().__init__(
            system_prompt="""You are a friendly study buddy. Help the user learn by:
1. Explaining concepts clearly
2. Asking follow-up questions to test understanding
3. Giving encouragement
4. Suggesting related topics to explore"""
        )

buddy = StudyBuddy()
print(buddy.chat("Help me understand recursion"))'''
    },
    {
        'marker': '# Exercise 2: Add message count',
        'hint': '''Track the count in the chatbot class:
1. Add a counter attribute in __init__
2. Increment it in the chat() method
3. Add a method to get stats''',
        'solution': '''class ChatbotWithStats(Chatbot):
    def __init__(self, system_prompt="You are a helpful assistant."):
        super().__init__(system_prompt)
        self.message_count = 0
        self.total_tokens = 0
    
    def chat(self, message: str) -> str:
        self.message_count += 1
        response = super().chat(message)
        return response
    
    def get_stats(self):
        return {
            "messages": self.message_count,
            "history_length": len(self.history)
        }

bot = ChatbotWithStats()
bot.chat("Hello!")
bot.chat("How are you?")
print(bot.get_stats())  # {"messages": 2, ...}'''
    }
]

# Week 3 exercises  
week3_exercises = [
    {
        'marker': '# Exercise 1: Create a recipe extractor',
        'hint': '''Define a Pydantic model for recipes:
- name: str
- ingredients: List[str]
- steps: List[str]
- prep_time_minutes: int
- difficulty: Literal["easy", "medium", "hard"]''',
        'solution': '''from pydantic import BaseModel
from typing import List, Literal

class Recipe(BaseModel):
    name: str
    ingredients: List[str]
    steps: List[str]
    prep_time_minutes: int
    difficulty: Literal["easy", "medium", "hard"]

def extract_recipe(text: str) -> Recipe:
    response = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Extract recipe information."},
            {"role": "user", "content": text}
        ],
        response_format=Recipe
    )
    return response.choices[0].message.parsed

recipe = extract_recipe("To make pasta: boil water, add pasta, cook 8 mins...")
print(recipe.model_dump_json(indent=2))'''
    },
    {
        'marker': '# Exercise 2: Multi-label classification',
        'hint': '''For multi-label, return a list of categories:
- Use List[str] in your model
- Or use a dict with boolean flags for each category''',
        'solution': '''class ContentLabels(BaseModel):
    categories: List[str]
    is_urgent: bool
    sentiment: Literal["positive", "negative", "neutral"]
    confidence: float

def classify_content(text: str) -> ContentLabels:
    response = client.beta.chat.completions.parse(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": "Classify the content."},
            {"role": "user", "content": text}
        ],
        response_format=ContentLabels
    )
    return response.choices[0].message.parsed

result = classify_content("URGENT: Server down! Need help immediately!")
print(result)  # categories=['technical', 'support'], is_urgent=True, ...'''
    }
]

if __name__ == "__main__":
    labs_dir = Path("labs")
    
    if not labs_dir.exists():
        print("Run this script from the ai-track-v2 directory")
        exit(1)
    
    # Week 1
    add_solution_cells(labs_dir / "week_01_first_api_call.ipynb", week1_exercises)
    
    # Week 2
    add_solution_cells(labs_dir / "week_02_chatbot.ipynb", week2_exercises)
    
    # Week 3
    add_solution_cells(labs_dir / "week_03_structured_output.ipynb", week3_exercises)
    
    # Week 4 - RAG Intro
    week4_exercises = [
        {
            'marker': 'def keyword_search',
            'hint': '''Keyword search is simple:
1. Split query into words
2. Count how many words appear in each document
3. Sort by count, return top results''',
            'solution': '''def keyword_search(query: str, docs: list, top_k: int = 2) -> list:
    query_words = set(query.lower().split())
    
    scored = []
    for doc in docs:
        doc_text = (doc['title'] + ' ' + doc['content']).lower()
        score = sum(1 for word in query_words if word in doc_text)
        scored.append((doc, score))
    
    scored.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scored[:top_k] if score > 0]'''
        }
    ]
    add_solution_cells(labs_dir / "week_04_rag_intro.ipynb", week4_exercises)
    
    # Week 5 - Embeddings
    week5_exercises = [
        {
            'marker': '# Exercise: Create a FAQ search',
            'hint': '''Build on the SemanticSearch class:
1. Add FAQ pairs (question + answer)  
2. Embed the questions only
3. On search, find similar questions
4. Return the answer for the matched question''',
            'solution': '''class FAQSearch:
    def __init__(self):
        self.faqs = []
        self.embeddings = []
    
    def add_faq(self, question: str, answer: str):
        embedding = get_embedding(question)
        self.faqs.append({"question": question, "answer": answer})
        self.embeddings.append(embedding)
    
    def search(self, query: str) -> dict:
        query_emb = get_embedding(query)
        scores = [cosine_similarity(query_emb, emb) for emb in self.embeddings]
        best_idx = scores.index(max(scores))
        return self.faqs[best_idx]

faq = FAQSearch()
faq.add_faq("How do I reset my password?", "Go to Settings > Security > Reset Password")
faq.add_faq("What are the office hours?", "9 AM to 5 PM, Monday to Friday")
result = faq.search("I forgot my password")
print(result["answer"])'''
        }
    ]
    add_solution_cells(labs_dir / "week_05_embeddings.ipynb", week5_exercises)
    
    # Week 6 - Production RAG  
    week6_exercises = [
        {
            'marker': 'def chunk_by_characters',
            'hint': '''Character chunking needs:
1. Loop through text in steps of (chunk_size - overlap)
2. Slice from current position to position + chunk_size
3. Collect all chunks in a list''',
            'solution': '''def chunk_by_characters(text: str, chunk_size: int = 500, overlap: int = 50) -> list:
    chunks = []
    step = chunk_size - overlap
    
    for i in range(0, len(text), step):
        chunk = text[i:i + chunk_size]
        if chunk:  # Don't add empty chunks
            chunks.append(chunk)
    
    return chunks

# Test it
text = "A" * 1000
chunks = chunk_by_characters(text, chunk_size=300, overlap=50)
print(f"Created {len(chunks)} chunks")'''
        }
    ]
    add_solution_cells(labs_dir / "week_06_production_rag.ipynb", week6_exercises)
    
    # Week 9 - Tool Calling
    week9_exercises = [
        {
            'marker': 'def get_weather',
            'hint': '''A weather function should:
1. Accept location and optional unit
2. Return a dict with temperature, condition, location
3. In real app, call a weather API''',
            'solution': '''def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get current weather for a location."""
    # In production, call a real weather API
    # This is a mock implementation
    weather_data = {
        "New York": {"temp": 22, "condition": "sunny"},
        "London": {"temp": 15, "condition": "cloudy"},
        "Tokyo": {"temp": 28, "condition": "humid"},
    }
    
    data = weather_data.get(location, {"temp": 20, "condition": "unknown"})
    
    if unit == "fahrenheit":
        data["temp"] = data["temp"] * 9/5 + 32
    
    return {
        "location": location,
        "temperature": data["temp"],
        "unit": unit,
        "condition": data["condition"]
    }'''
        }
    ]
    add_solution_cells(labs_dir / "week_09_tool_calling.ipynb", week9_exercises)
    
    # Week 12 - Data Engineering
    week12_exercises = [
        {
            'marker': '# Exercise 1: SQL - Retrieval success rate',
            'hint': '''To calculate success rate:
1. COUNT all queries
2. COUNT queries where feedback = "helpful"
3. Divide and multiply by 100 for percentage''',
            'solution': '''SELECT 
    COUNT(*) as total_queries,
    SUM(CASE WHEN feedback = 'helpful' THEN 1 ELSE 0 END) as successful,
    ROUND(100.0 * SUM(CASE WHEN feedback = 'helpful' THEN 1 ELSE 0 END) / COUNT(*), 2) as success_rate
FROM rag_queries
WHERE timestamp >= date('now', '-7 days');'''
        }
    ]
    add_solution_cells(labs_dir / "week_12_data_engineering.ipynb", week12_exercises)
    
    print("\n✓ All labs updated with hints and solutions!")
