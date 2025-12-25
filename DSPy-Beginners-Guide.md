# DSPy Beginner's Guide

**Date:** December 24, 2025

A beginner-friendly introduction to DSPy - the framework for programming language models instead of prompting them.

---

## Table of Contents

1. [What is DSPy?](#what-is-dspy)
2. [Why DSPy? The Problem It Solves](#why-dspy-the-problem-it-solves)
3. [Core Philosophy](#core-philosophy)
4. [Installation and Setup](#installation-and-setup)
5. [Key Concepts](#key-concepts)
   - [Signatures](#signatures)
   - [Modules](#modules)
   - [Optimizers (Compilers)](#optimizers-compilers)
6. [Benefits of DSPy](#benefits-of-dspy)
7. [Limitations of DSPy](#limitations-of-dspy)
8. [Your First DSPy Program](#your-first-dspy-program)
9. [Example 1: Question Answering with Chain of Thought](#example-1-question-answering-with-chain-of-thought)
10. [Example 2: Simple RAG Application](#example-2-simple-rag-application)
11. [Example 3: Classification with Optimization](#example-3-classification-with-optimization)
12. [Next Steps](#next-steps)

---

## What is DSPy?

**DSPy** (Declarative Self-improving Python) is a framework for programming language models developed by Stanford NLP. Instead of writing and tweaking prompts manually, you write Python code that declares what you want, and DSPy figures out how to achieve it.

Think of DSPy as the difference between:
- **Traditional prompting**: Writing detailed instructions in natural language and hoping the LLM follows them
- **DSPy**: Writing structured Python code that defines inputs, outputs, and logic, then letting DSPy optimize the prompts automatically

### The Core Idea

```
Traditional: "You are a helpful assistant. Given a question, provide a concise answer..."

DSPy: question -> answer
```

DSPy separates **what you want** (the signature) from **how to achieve it** (the optimization). You define the task declaratively, and DSPy generates and refines the prompts behind the scenes.

---

## Why DSPy? The Problem It Solves

### The Prompt Engineering Problem

Traditional LLM development suffers from several pain points:

1. **Fragile Prompts**: Small changes to prompts can cause unpredictable behavior
2. **Manual Iteration**: Engineers spend hours tweaking prompts through trial and error
3. **Non-Transferable**: Prompts optimized for one model often fail on another
4. **Hard to Maintain**: Complex prompts become difficult to understand and modify
5. **No Systematic Improvement**: No clear path to improve prompt quality over time

### How DSPy Helps

DSPy addresses these issues by:

1. **Programmatic Approach**: Write Python code instead of prompt strings
2. **Automatic Optimization**: DSPy generates and refines prompts for you
3. **Modular Design**: Build complex systems from simple, reusable components
4. **Model Agnostic**: Switch between models without rewriting prompts
5. **Systematic Improvement**: Use metrics and optimizers to improve quality

---

## Core Philosophy

DSPy is built on three key principles:

### 1. Signatures Over Prompts

Instead of writing:
```
"Given a document, summarize it in 2-3 sentences. Be concise and capture the main points..."
```

You write:
```python
summarize = dspy.Predict('document -> summary')
```

The signature `document -> summary` declares the transformation you want. DSPy handles the prompt engineering.

### 2. Modules Over Scripts

DSPy programs are built from composable modules, similar to PyTorch neural networks:

```python
class MyProgram(dspy.Module):
    def __init__(self):
        self.step1 = dspy.ChainOfThought('question -> reasoning')
        self.step2 = dspy.Predict('reasoning -> answer')

    def forward(self, question):
        reasoning = self.step1(question=question).reasoning
        return self.step2(reasoning=reasoning)
```

### 3. Optimization Over Guessing

Instead of manually tweaking prompts, you:
1. Define a metric (what "good" looks like)
2. Provide training examples
3. Let DSPy's optimizers find the best prompts

---

## Installation and Setup

### Installation

```bash
# Using uv (recommended)
uv add dspy

# Or with pip
pip install dspy
```

### Configure a Language Model

DSPy supports many LLM providers. Set up your preferred one:

#### OpenAI

```python
import os
import dspy

# Set your API key
os.environ['OPENAI_API_KEY'] = 'your-api-key'

# Configure DSPy to use OpenAI
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)
```

#### Anthropic (Claude)

```python
import dspy

lm = dspy.LM('anthropic/claude-sonnet-4-5-20250929', api_key='YOUR_ANTHROPIC_API_KEY')
dspy.configure(lm=lm)
```

#### Local Models with Ollama

```bash
# First, install and run Ollama
curl -fsSL https://ollama.ai/install.sh | sh
ollama run llama3.2:1b
```

```python
import dspy

lm = dspy.LM('ollama_chat/llama3.2:1b', api_base='http://localhost:11434', api_key='')
dspy.configure(lm=lm)
```

#### Multiple Models (e.g., Teacher-Student)

```python
import dspy

# Main model (student)
llama = dspy.LM('ollama_chat/llama3.2', api_base='http://localhost:11434')

# Teacher model for optimization
gpt4o = dspy.LM('openai/gpt-4o', temperature=0.7)

# Set the default
dspy.configure(lm=llama)
```

---

## Key Concepts

### Signatures

A **Signature** defines the input-output behavior of a module. It's the contract between you and DSPy.

#### Inline Signatures (Simple)

```python
# Basic format: inputs -> outputs
classify = dspy.Predict('sentence -> sentiment: bool')
summarize = dspy.Predict('document -> summary')
translate = dspy.Predict('text, target_language -> translation')
```

#### Class-Based Signatures (More Control)

```python
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""

    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="often between 1 and 5 words")
```

#### Signatures with Instructions

```python
toxicity = dspy.Predict(
    dspy.Signature(
        "comment -> toxic: bool",
        instructions="Mark as 'toxic' if the comment includes insults, harassment, or sarcastic derogatory remarks.",
    )
)
```

### Modules

**Modules** are the building blocks that use signatures. DSPy provides several built-in modules:

#### dspy.Predict

The most basic module - just runs the signature:

```python
# Declare
classify = dspy.Predict('sentence -> sentiment: bool')

# Use
result = classify(sentence="I love this product!")
print(result.sentiment)  # True
```

#### dspy.ChainOfThought

Adds reasoning before the answer (like "think step by step"):

```python
# The module automatically adds a 'reasoning' field
cot = dspy.ChainOfThought('question -> answer')

result = cot(question="What is 15% of 80?")
print(result.reasoning)  # "To find 15% of 80, I multiply 80 by 0.15..."
print(result.answer)     # "12"
```

#### dspy.ReAct

An agent that can use tools to answer questions:

```python
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information."""
    # ... implementation ...
    return "search results"

def calculate(expression: str) -> float:
    """Evaluate a math expression."""
    return eval(expression)

react = dspy.ReAct("question -> answer", tools=[search_wikipedia, calculate])
result = react(question="What is the population of France divided by 1000?")
```

#### Custom Modules

Combine modules to build complex programs:

```python
class ArticleDrafter(dspy.Module):
    def __init__(self):
        self.outline = dspy.ChainOfThought('topic -> title, sections: list[str]')
        self.draft = dspy.ChainOfThought('topic, section_heading -> content')

    def forward(self, topic):
        outline = self.outline(topic=topic)
        sections = []
        for heading in outline.sections:
            section = self.draft(topic=outline.title, section_heading=heading)
            sections.append(section.content)
        return dspy.Prediction(title=outline.title, sections=sections)
```

### Optimizers (Compilers)

**Optimizers** automatically improve your program by finding better prompts and examples.

#### LabeledFewShot

Uses provided examples as few-shot demonstrations:

```python
from dspy.teleprompt import LabeledFewShot

optimizer = LabeledFewShot(k=8)  # Use 8 examples
optimized_program = optimizer.compile(
    student=my_program,
    trainset=training_data
)
```

#### BootstrapFewShot

Self-generates examples by running the program and keeping successful ones:

```python
from dspy.teleprompt import BootstrapFewShot

optimizer = BootstrapFewShot(
    metric=my_metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=16
)
optimized_program = optimizer.compile(
    student=my_program,
    trainset=training_data
)
```

#### MIPROv2

A powerful multi-stage optimizer:

```python
from dspy.teleprompt import MIPROv2

optimizer = MIPROv2(
    metric=my_metric,
    auto="light"  # Options: "light", "medium", "heavy"
)
optimized_program = optimizer.compile(
    my_program.deepcopy(),
    trainset=training_data
)
```

---

## Benefits of DSPy

### 1. Separation of Concerns

DSPy separates **what** you want from **how** to achieve it:
- You define the task structure (signatures)
- DSPy handles prompt engineering

### 2. Automatic Optimization

Instead of manual prompt tweaking:
- Define a metric (what "good" means)
- Provide training data
- Let optimizers find the best prompts

### 3. Modularity and Reusability

Build complex systems from simple, testable components:
- Each module has a clear interface
- Modules can be composed, tested, and optimized independently

### 4. Model Portability

Switch between LLM providers without rewriting prompts:
```python
# Just change the configuration
dspy.configure(lm=dspy.LM('openai/gpt-4o'))
# ... or ...
dspy.configure(lm=dspy.LM('anthropic/claude-sonnet-4-5-20250929'))
```

### 5. Systematic Evaluation

Built-in support for metrics and evaluation:
```python
from dspy.evaluate import Evaluate

evaluate = Evaluate(devset=dev_data, metric=my_metric, num_threads=4)
score = evaluate(my_program)
```

### 6. Reproducibility

Programs are code, not prompt strings:
- Version control friendly
- Easier to debug and test
- Clear documentation of logic

---

## Limitations of DSPy

### 1. Learning Curve

- Requires understanding new concepts (signatures, modules, optimizers)
- Different mindset from traditional prompt engineering
- Documentation can be sparse for advanced features

### 2. Optimization Costs

- Optimization runs consume many API calls
- Can be expensive with paid LLM APIs
- Heavy optimization modes take significant time

### 3. Debugging Complexity

- Understanding why a program fails can be harder
- Optimization is somewhat opaque ("black box")
- Tracing issues through compiled programs is challenging

### 4. Not Always Necessary

- Simple, one-off prompts may not benefit from DSPy
- Adds complexity for trivial tasks
- Manual prompts might work well for stable, simple use cases

### 5. Maturity

- Relatively new framework (still evolving)
- API may change between versions
- Smaller community compared to frameworks like LangChain

### When to Use DSPy

**Good fit:**
- Complex multi-step LLM workflows
- Systems requiring systematic improvement
- Production applications needing reliability
- Projects with clear evaluation metrics

**Maybe skip:**
- Simple one-shot prompts
- Quick prototypes
- Tasks without clear success metrics

---

## Your First DSPy Program

Let's build a simple sentiment classifier:

```python
import dspy

# 1. Configure the LM
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

# 2. Create a simple classifier using Predict
classify = dspy.Predict('sentence -> sentiment: bool')

# 3. Use it
result = classify(sentence="I absolutely love this movie!")
print(f"Sentiment: {'Positive' if result.sentiment else 'Negative'}")

# Try another one
result = classify(sentence="This was a terrible waste of time.")
print(f"Sentiment: {'Positive' if result.sentiment else 'Negative'}")
```

That's it! In just a few lines, you have a working sentiment classifier without writing any prompts.

---

## Example 1: Question Answering with Chain of Thought

This example shows how to use ChainOfThought for better reasoning:

```python
import dspy

# Configure the language model
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

# Define a signature for QA
class BasicQA(dspy.Signature):
    """Answer questions with short factoid answers."""
    question: str = dspy.InputField()
    answer: str = dspy.OutputField(desc="often between 1 and 5 words")

# Create a ChainOfThought module
qa = dspy.ChainOfThought(BasicQA)

# Ask a question
result = qa(question="What is the capital of France?")
print(f"Reasoning: {result.reasoning}")
print(f"Answer: {result.answer}")

# Try a math question
math_qa = dspy.ChainOfThought("question -> answer: float")
result = math_qa(question="If a car travels 60 miles in 1.5 hours, what is its average speed in mph?")
print(f"Reasoning: {result.reasoning}")
print(f"Answer: {result.answer}")
```

**Output:**
```
Reasoning: The capital of France is a well-known fact. France is a country in Western Europe, and its capital city is Paris.
Answer: Paris

Reasoning: To find average speed, I divide distance by time. 60 miles / 1.5 hours = 40 mph.
Answer: 40.0
```

---

## Example 2: Simple RAG Application

This example demonstrates a Retrieval-Augmented Generation (RAG) system:

```python
import dspy

# Configure the language model
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

# Simulated knowledge base (in practice, use a real retriever)
knowledge_base = {
    "python": "Python is a high-level programming language known for its readability and versatility. It was created by Guido van Rossum and released in 1991.",
    "javascript": "JavaScript is a programming language that enables interactive web pages. It was created by Brendan Eich in 1995.",
    "rust": "Rust is a systems programming language focused on safety and performance. It was first released in 2010 by Mozilla.",
}

def search(query: str) -> str:
    """Simple keyword-based search."""
    query_lower = query.lower()
    for key, value in knowledge_base.items():
        if key in query_lower:
            return value
    return "No relevant information found."

# Define the RAG module
class SimpleRAG(dspy.Module):
    def __init__(self):
        self.respond = dspy.ChainOfThought('context, question -> answer')

    def forward(self, question):
        # Retrieve relevant context
        context = search(question)
        # Generate response using context
        return self.respond(context=context, question=question)

# Create and use the RAG system
rag = SimpleRAG()

# Ask questions
questions = [
    "Who created Python?",
    "When was JavaScript released?",
    "What is Rust focused on?",
]

for question in questions:
    result = rag(question=question)
    print(f"Q: {question}")
    print(f"A: {result.answer}\n")
```

**Output:**
```
Q: Who created Python?
A: Guido van Rossum

Q: When was JavaScript released?
A: 1995

Q: What is Rust focused on?
A: Safety and performance
```

---

## Example 3: Classification with Optimization

This example shows how to use DSPy's optimization capabilities:

```python
import dspy
from dspy.teleprompt import BootstrapFewShot

# Configure the language model
lm = dspy.LM('openai/gpt-4o-mini')
dspy.configure(lm=lm)

# Define training data
trainset = [
    dspy.Example(text="I love this product!", label="positive").with_inputs("text"),
    dspy.Example(text="Terrible experience, never again.", label="negative").with_inputs("text"),
    dspy.Example(text="Best purchase I've ever made!", label="positive").with_inputs("text"),
    dspy.Example(text="Waste of money.", label="negative").with_inputs("text"),
    dspy.Example(text="Exceeded my expectations!", label="positive").with_inputs("text"),
    dspy.Example(text="Broke after one day.", label="negative").with_inputs("text"),
    dspy.Example(text="Highly recommend!", label="positive").with_inputs("text"),
    dspy.Example(text="Don't buy this.", label="negative").with_inputs("text"),
]

# Define development set for evaluation
devset = [
    dspy.Example(text="Amazing quality!", label="positive").with_inputs("text"),
    dspy.Example(text="Complete disappointment.", label="negative").with_inputs("text"),
]

# Create the classifier
class SentimentClassifier(dspy.Module):
    def __init__(self):
        self.classify = dspy.Predict('text -> label')

    def forward(self, text):
        return self.classify(text=text)

# Define a metric
def accuracy_metric(example, pred, trace=None):
    return example.label.lower() == pred.label.lower()

# Create the optimizer
optimizer = BootstrapFewShot(
    metric=accuracy_metric,
    max_bootstrapped_demos=4,
    max_labeled_demos=4,
)

# Compile (optimize) the program
classifier = SentimentClassifier()
optimized_classifier = optimizer.compile(
    student=classifier,
    trainset=trainset,
)

# Test the optimized classifier
test_texts = [
    "This is fantastic!",
    "I regret buying this.",
    "Worth every penny!",
]

print("Testing optimized classifier:")
for text in test_texts:
    result = optimized_classifier(text=text)
    print(f"  '{text}' -> {result.label}")

# Evaluate on dev set
from dspy.evaluate import Evaluate

evaluator = Evaluate(devset=devset, metric=accuracy_metric, num_threads=1, display_progress=False)
score = evaluator(optimized_classifier)
print(f"\nDev set accuracy: {score}%")
```

---

## Next Steps

Now that you understand the basics of DSPy, here are some paths to continue learning:

### 1. Explore More Modules

- **dspy.ProgramOfThought**: For complex multi-step reasoning
- **dspy.ReAct**: For agent-based applications with tools
- **dspy.Refine**: For iterative improvement of outputs

### 2. Learn Advanced Optimization

- **MIPROv2**: Multi-stage instruction and prompt optimization
- **BootstrapFewShotWithRandomSearch**: More thorough example selection
- **SIMBA**: Newer optimization algorithm

### 3. Build Real Applications

- **RAG systems**: With real vector databases (FAISS, ChromaDB)
- **Agents**: That use multiple tools
- **Multi-hop QA**: Complex reasoning over multiple documents

### 4. Resources

- **Official Documentation**: https://dspy.ai
- **GitHub Repository**: https://github.com/stanfordnlp/dspy
- **Tutorials**: https://dspy.ai/tutorials

---

## Summary

| Concept | Description |
|---------|-------------|
| **Signature** | Declares input/output contract (`question -> answer`) |
| **Module** | Building block that uses signatures (`dspy.Predict`, `dspy.ChainOfThought`) |
| **Optimizer** | Automatically improves prompts (`BootstrapFewShot`, `MIPROv2`) |
| **Metric** | Defines what "good" means for your task |
| **Example** | Training/evaluation data point with inputs and labels |

### Key Takeaways

1. **Write code, not prompts**: Define what you want with signatures, let DSPy handle the prompts
2. **Build modularly**: Compose simple modules into complex programs
3. **Optimize systematically**: Use metrics and training data to improve automatically
4. **Iterate in stages**: Start with programming, add evaluation, then optimize

DSPy represents a paradigm shift from prompt engineering to LLM programming. While it has a learning curve, the benefits of modularity, optimization, and maintainability make it powerful for building production-grade LLM applications.
