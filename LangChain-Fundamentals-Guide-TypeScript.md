# LangChain.js Fundamentals Guide (TypeScript)

**Date:** December 24, 2025

This guide provides comprehensive instructions on using LangChain.js with TypeScript to communicate with various LLMs, build simple chat applications, use chains, templates, and runnables.

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Connecting to LLMs](#connecting-to-llms)
   - [Using initChatModel](#using-initchatmodel)
   - [Provider-Specific Classes](#provider-specific-classes)
   - [Configuration Parameters](#configuration-parameters)
4. [Messages and Conversations](#messages-and-conversations)
   - [Message Types](#message-types)
   - [Creating Messages](#creating-messages)
   - [Conversation History](#conversation-history)
5. [Building a Simple Chat Application](#building-a-simple-chat-application)
   - [Basic Invocation](#basic-invocation)
   - [Simple Chat Loop](#simple-chat-loop)
6. [Streaming Responses](#streaming-responses)
   - [Basic Streaming](#basic-streaming)
   - [Streaming with Callbacks](#streaming-with-callbacks)
7. [Prompt Templates](#prompt-templates)
   - [String Templates](#string-templates)
   - [Chat Prompt Templates](#chat-prompt-templates)
   - [Messages Placeholder](#messages-placeholder)
8. [Chains and Runnables](#chains-and-runnables)
   - [Creating Chains with Pipe](#creating-chains-with-pipe)
   - [RunnableLambda](#runnablelambda)
   - [RunnableSequence](#runnablesequence)
9. [Structured Output](#structured-output)
   - [Using Zod Schemas](#using-zod-schemas)
   - [Nested Schemas](#nested-schemas)
   - [With Agents](#with-agents)
10. [Tool Integration](#tool-integration)
    - [Defining Tools](#defining-tools)
    - [Binding Tools to Models](#binding-tools-to-models)
11. [Complete Examples](#complete-examples)
12. [Best Practices](#best-practices)

---

## Overview

**LangChain.js** is the JavaScript/TypeScript version of the LangChain framework for developing applications powered by large language models (LLMs). It provides:

- **Unified interfaces** for multiple LLM providers (OpenAI, Anthropic, Google, AWS, etc.)
- **TypeScript-first design** with full type safety
- **Modular components** for building complex LLM workflows
- **Streaming support** for real-time responses
- **Zod integration** for structured output validation

This guide focuses on LangChain.js core capabilities for TypeScript developers.

---

## Installation

### Setting Up Your Project

```bash
# Create a new Node.js project
mkdir my-langchain-project
cd my-langchain-project

# Initialize with npm
npm init -y

# Or with pnpm/yarn
pnpm init
yarn init -y
```

### TypeScript Configuration

```bash
# Install TypeScript
npm install typescript ts-node @types/node --save-dev

# Initialize TypeScript configuration
npx tsc --init
```

Update your `tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "esModuleInterop": true,
    "strict": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src/**/*"]
}
```

### Core LangChain Packages

```bash
# Core LangChain package
npm install langchain @langchain/core
```

### Provider-Specific Packages

```bash
# OpenAI
npm install @langchain/openai

# Anthropic (Claude)
npm install @langchain/anthropic

# Google Gemini
npm install @langchain/google-genai

# Google Vertex AI
npm install @langchain/google-vertexai

# AWS Bedrock
npm install @langchain/aws

# Ollama (Local Models)
npm install @langchain/ollama

# Mistral AI
npm install @langchain/mistralai

# Cohere
npm install @langchain/cohere

# Community integrations
npm install @langchain/community
```

### Additional Dependencies

```bash
# Zod for schema validation (required for structured output)
npm install zod
```

### Running TypeScript Files

```bash
# Using ts-node
npx ts-node src/index.ts

# Or add to package.json scripts
# "scripts": { "start": "ts-node src/index.ts" }
npm start
```

---

## Connecting to LLMs

### Using initChatModel

The `initChatModel` function provides a unified way to initialize chat models:

```typescript
import { initChatModel } from "langchain";

// Set environment variable
process.env.OPENAI_API_KEY = "your-api-key";

// Initialize OpenAI
const model = await initChatModel("gpt-4.1");

// Initialize with provider prefix
const claudeModel = await initChatModel("anthropic:claude-sonnet-4-5-20250929");
const geminiModel = await initChatModel("google_genai:gemini-2.5-flash-lite");

// Azure OpenAI
process.env.AZURE_OPENAI_API_KEY = "your-api-key";
process.env.AZURE_OPENAI_ENDPOINT = "your-endpoint";
process.env.OPENAI_API_VERSION = "2025-03-01-preview";
const azureModel = await initChatModel("azure_openai:gpt-4.1");

// AWS Bedrock
const bedrockModel = await initChatModel("bedrock:gpt-4.1");
```

### Provider-Specific Classes

For more control, use provider-specific classes:

#### OpenAI

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-4o-mini",
  temperature: 0,
  apiKey: process.env.OPENAI_API_KEY,
});

const response = await model.invoke("Hello, world!");
console.log(response.content);
```

#### Anthropic (Claude)

```typescript
import { ChatAnthropic } from "@langchain/anthropic";

const model = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const response = await model.invoke("Hello, world!");
```

#### Google Gemini

```typescript
import { ChatGoogleGenerativeAI } from "@langchain/google-genai";

const model = new ChatGoogleGenerativeAI({
  modelName: "gemini-2.5-flash-lite",
  temperature: 0,
  apiKey: process.env.GOOGLE_API_KEY,
});
```

#### Ollama (Local)

```typescript
import { ChatOllama } from "@langchain/ollama";

const model = new ChatOllama({
  model: "llama3.2",
  baseUrl: "http://localhost:11434",
});
```

#### Mistral AI

```typescript
import { ChatMistralAI } from "@langchain/mistralai";

const model = new ChatMistralAI({
  model: "mistral-large-latest",
  temperature: 0,
  apiKey: process.env.MISTRAL_API_KEY,
});
```

### Supported LLM Providers

| Provider | Package | Model Examples |
|----------|---------|----------------|
| OpenAI | `@langchain/openai` | gpt-4o, gpt-4o-mini |
| Anthropic | `@langchain/anthropic` | claude-sonnet-4-5, claude-haiku |
| Google Gemini | `@langchain/google-genai` | gemini-2.5-flash-lite |
| Google Vertex | `@langchain/google-vertexai` | gemini-2.5-flash |
| AWS Bedrock | `@langchain/aws` | claude-3-5-sonnet |
| Mistral | `@langchain/mistralai` | mistral-large-latest |
| Ollama | `@langchain/ollama` | llama3.2, mistral |
| Cohere | `@langchain/cohere` | command-r-plus |

### Configuration Parameters

```typescript
const model = await initChatModel("claude-sonnet-4-5-20250929", {
  temperature: 0.7,    // Controls randomness (0.0-1.0)
  timeout: 30,         // Maximum seconds to wait
  max_tokens: 1000,    // Maximum tokens in response
});
```

---

## Messages and Conversations

### Message Types

LangChain.js provides typed message classes:

```typescript
import {
  HumanMessage,
  AIMessage,
  SystemMessage,
  ToolMessage,
} from "@langchain/core/messages";

// System message - sets behavior
const systemMsg = new SystemMessage("You are a helpful assistant.");

// Human message - user input
const humanMsg = new HumanMessage("Hello, how are you?");

// AI message - model response
const aiMsg = new AIMessage("I'm doing well, thank you!");

// Tool message - tool execution result
const toolMsg = new ToolMessage({
  content: "Result from tool",
  tool_call_id: "call_123",
});
```

### Creating Messages

#### Using Message Objects

```typescript
import { initChatModel, HumanMessage, SystemMessage } from "langchain";

const model = await initChatModel("gpt-4o-mini");

const systemMsg = new SystemMessage("You are a helpful assistant.");
const humanMsg = new HumanMessage("Hello, how are you?");

const messages = [systemMsg, humanMsg];
const response = await model.invoke(messages);

console.log(response.content);
```

#### Using Object Literals

```typescript
const response = await model.invoke([
  { role: "system", content: "You are a helpful assistant." },
  { role: "user", content: "Hello, how are you?" },
]);
```

### Conversation History

Maintain context across turns:

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, AIMessage, SystemMessage } from "@langchain/core/messages";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

// Maintain message history
const messages: (SystemMessage | HumanMessage | AIMessage)[] = [
  new SystemMessage("You are a helpful assistant. Be concise."),
];

async function chat(userInput: string): Promise<string> {
  // Add user message
  messages.push(new HumanMessage(userInput));

  // Get response
  const response = await model.invoke(messages);

  // Add to history
  messages.push(response);

  return response.content as string;
}

// Example usage
console.log(await chat("Hello! My name is Alice."));
console.log(await chat("What's my name?"));  // Will remember "Alice"
```

---

## Building a Simple Chat Application

### Basic Invocation

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

// Simple text prompt
const response = await model.invoke("Write a haiku about TypeScript");
console.log(response.content);
```

### Simple Chat Loop

A complete interactive chat application:

```typescript
import * as readline from "readline";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, AIMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";

async function runChat() {
  // Ensure API key is set
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY environment variable is required");
  }

  const model = new ChatOpenAI({ model: "gpt-4o-mini" });

  const messages: BaseMessage[] = [
    new SystemMessage("You are a helpful, friendly assistant. Be concise."),
  ];

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log("Chat started. Type 'quit' to exit.\n");

  const askQuestion = () => {
    rl.question("You: ", async (userInput) => {
      const trimmedInput = userInput.trim();

      if (trimmedInput.toLowerCase() === "quit") {
        console.log("Goodbye!");
        rl.close();
        return;
      }

      if (!trimmedInput) {
        askQuestion();
        return;
      }

      // Add user message
      messages.push(new HumanMessage(trimmedInput));

      try {
        // Get response
        const response = await model.invoke(messages);
        messages.push(response);

        console.log(`Assistant: ${response.content}\n`);
      } catch (error) {
        console.error("Error:", error);
      }

      askQuestion();
    });
  };

  askQuestion();
}

runChat();
```

---

## Streaming Responses

### Basic Streaming

Stream tokens as they are generated:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

// Stream the response
const stream = await model.stream("Write a short poem about coding");

for await (const chunk of stream) {
  process.stdout.write(chunk.content as string);
}
console.log(); // New line at end
```

### Streaming with Callbacks

Use callbacks for more control:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({
  model: "gpt-4o-mini",
  streaming: true,
});

await model.invoke("Tell me a joke", {
  callbacks: [
    {
      handleLLMNewToken(token: string) {
        process.stdout.write(token);
      },
      handleLLMEnd() {
        console.log("\n--- Generation complete ---");
      },
    },
  ],
});
```

### Streaming with AbortController

Cancel long-running requests:

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

const controller = new AbortController();

// Cancel after 5 seconds
setTimeout(() => {
  controller.abort();
  console.log("\nAborted!");
}, 5000);

try {
  await model.invoke("Write a very long story", {
    signal: controller.signal,
    callbacks: [
      {
        handleLLMNewToken(token: string) {
          process.stdout.write(token);
        },
      },
    ],
  });
} catch (error) {
  if ((error as Error).name === "AbortError") {
    console.log("Request was cancelled");
  }
}
```

---

## Prompt Templates

### String Templates

Create reusable prompt templates:

```typescript
import { PromptTemplate } from "@langchain/core/prompts";

const template = PromptTemplate.fromTemplate(
  "Translate the following text to {language}: {text}"
);

const prompt = await template.invoke({
  language: "French",
  text: "Hello, how are you?",
});

console.log(prompt.toString());
// Output: Translate the following text to French: Hello, how are you?
```

### Chat Prompt Templates

For multi-message prompts:

```typescript
import { ChatPromptTemplate } from "@langchain/core/prompts";

const chatTemplate = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant that translates {input_language} to {output_language}."],
  ["human", "{text}"],
]);

const messages = await chatTemplate.invoke({
  input_language: "English",
  output_language: "Spanish",
  text: "Hello, how are you?",
});

// Use with a model
const response = await model.invoke(messages);
```

### Messages Placeholder

Insert dynamic message arrays:

```typescript
import {
  ChatPromptTemplate,
  MessagesPlaceholder,
} from "@langchain/core/prompts";
import { HumanMessage } from "@langchain/core/messages";

const template = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant"],
  new MessagesPlaceholder("history"),
  ["human", "{input}"],
]);

const messages = await template.invoke({
  history: [
    new HumanMessage("Hi, my name is Bob"),
    // ... previous messages
  ],
  input: "What's my name?",
});
```

### Escaping Curly Braces

When including JSON in templates, escape with double braces:

```typescript
import { PromptTemplate } from "@langchain/core/prompts";

const template = PromptTemplate.fromTemplate(`
You are a helpful assistant.

Here is an example response format:
{{
  "name": "John",
  "age": 30
}}

Now answer this question: {question}
`);
```

---

## Chains and Runnables

### Creating Chains with Pipe

Use the `.pipe()` method to chain components:

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant"],
  ["human", "Tell me a joke about {topic}"],
]);

const model = new ChatOpenAI({ model: "gpt-4o-mini" });
const outputParser = new StringOutputParser();

// Chain: prompt -> model -> parser
const chain = prompt.pipe(model).pipe(outputParser);

const result = await chain.invoke({ topic: "programming" });
console.log(result);
```

### RunnableLambda

Create custom runnable functions:

```typescript
import { RunnableLambda } from "@langchain/core/runnables";

// Transform function
const toUpperCase = new RunnableLambda({
  func: (input: string) => input.toUpperCase(),
});

// Use in a chain
const result = await toUpperCase.invoke("hello world");
console.log(result); // "HELLO WORLD"
```

### RunnableSequence

Compose multiple runnables:

```typescript
import { RunnableSequence, RunnableLambda } from "@langchain/core/runnables";
import { ChatOpenAI } from "@langchain/openai";
import { StringOutputParser } from "@langchain/core/output_parsers";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

const chain = RunnableSequence.from([
  new RunnableLambda({
    func: (topic: string) => `Tell me a fun fact about ${topic}`,
  }),
  model,
  new StringOutputParser(),
]);

const result = await chain.invoke("TypeScript");
console.log(result);
```

### Complex Chain Example

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { RunnableLambda } from "@langchain/core/runnables";
import { HumanMessage } from "@langchain/core/messages";

const llm = new ChatOpenAI({ model: "gpt-4o" });

const prompt = ChatPromptTemplate.fromMessages([
  ["system", "You are a helpful assistant."],
  ["placeholder", "{messages}"],
]);

const llmWithTools = llm.bindTools([myTool]);
const chain = prompt.pipe(llmWithTools);

const toolChain = RunnableLambda.from(async (userInput: string, config) => {
  const humanMessage = new HumanMessage(userInput);

  const aiMsg = await chain.invoke(
    { messages: [new HumanMessage(userInput)] },
    config
  );

  const toolMsgs = await myTool.batch(aiMsg.tool_calls, config);

  return chain.invoke(
    { messages: [humanMessage, aiMsg, ...toolMsgs] },
    config
  );
});

const result = await toolChain.invoke("What's the weather in SF?");
```

---

## Structured Output

### Using Zod Schemas

Get type-safe structured responses:

```typescript
import * as z from "zod";
import { ChatOpenAI } from "@langchain/openai";

// Define the schema
const Movie = z.object({
  title: z.string().describe("The title of the movie"),
  year: z.number().describe("The year the movie was released"),
  director: z.string().describe("The director of the movie"),
  rating: z.number().describe("The movie's rating out of 10"),
});

const model = new ChatOpenAI({ model: "gpt-4o-mini" });
const modelWithStructure = model.withStructuredOutput(Movie);

const response = await modelWithStructure.invoke(
  "Provide details about the movie Inception"
);

console.log(response);
// {
//   title: "Inception",
//   year: 2010,
//   director: "Christopher Nolan",
//   rating: 8.8,
// }

// TypeScript knows the type!
console.log(response.title);  // Type-safe access
```

### Nested Schemas

For complex data structures:

```typescript
import * as z from "zod";

const Actor = z.object({
  name: z.string(),
  role: z.string(),
});

const MovieDetails = z.object({
  title: z.string(),
  year: z.number(),
  cast: z.array(Actor),
  genres: z.array(z.string()),
  budget: z.number().nullable().describe("Budget in millions USD"),
});

const modelWithStructure = model.withStructuredOutput(MovieDetails);
const response = await modelWithStructure.invoke(
  "Tell me about The Dark Knight"
);
```

### With Agents

Use structured output with agents:

```typescript
import * as z from "zod";
import { createAgent } from "langchain";

const ContactInfo = z.object({
  name: z.string(),
  email: z.string(),
  phone: z.string(),
});

const agent = createAgent({
  model: "gpt-4o",
  responseFormat: ContactInfo,
});

const result = await agent.invoke({
  messages: [
    {
      role: "user",
      content: "Extract contact info from: John Doe, john@example.com, (555) 123-4567",
    },
  ],
});

console.log(result.structuredResponse);
// {
//   name: 'John Doe',
//   email: 'john@example.com',
//   phone: '(555) 123-4567'
// }
```

---

## Tool Integration

### Defining Tools

Create tools with Zod schemas:

```typescript
import * as z from "zod";
import { tool } from "@langchain/core/tools";

const getWeather = tool(
  async ({ location }) => {
    // In production, call a real weather API
    return `The weather in ${location} is sunny and 72F`;
  },
  {
    name: "get_weather",
    description: "Get the current weather in a given location",
    schema: z.object({
      location: z.string().describe("The city and state, e.g. San Francisco, CA"),
    }),
  }
);

const searchDatabase = tool(
  async ({ query, limit }) => {
    return `Found ${limit} results for '${query}'`;
  },
  {
    name: "search_database",
    description: "Search the customer database for records matching the query",
    schema: z.object({
      query: z.string().describe("Search terms to look for"),
      limit: z.number().describe("Maximum number of results to return"),
    }),
  }
);
```

### Binding Tools to Models

```typescript
import { ChatOpenAI } from "@langchain/openai";

const model = new ChatOpenAI({ model: "gpt-4o-mini" });

// Bind tools to the model
const modelWithTools = model.bindTools([getWeather, searchDatabase]);

// Invoke and check for tool calls
const response = await modelWithTools.invoke(
  "What's the weather in Boston?"
);

if (response.tool_calls && response.tool_calls.length > 0) {
  for (const toolCall of response.tool_calls) {
    console.log(`Tool: ${toolCall.name}`);
    console.log(`Args: ${JSON.stringify(toolCall.args)}`);
  }
}
```

### Complete Tool Example

```typescript
import * as z from "zod";
import { ChatAnthropic } from "@langchain/anthropic";
import { tool } from "@langchain/core/tools";

// Define tools
const add = tool(
  ({ a, b }) => (a + b).toString(),
  {
    name: "add",
    description: "Add two numbers together",
    schema: z.object({
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);

const multiply = tool(
  ({ a, b }) => (a * b).toString(),
  {
    name: "multiply",
    description: "Multiply two numbers",
    schema: z.object({
      a: z.number().describe("First number"),
      b: z.number().describe("Second number"),
    }),
  }
);

// Create model with tools
const model = new ChatAnthropic({
  model: "claude-sonnet-4-5-20250929",
  temperature: 0,
});

const tools = [add, multiply];
const toolsByName = Object.fromEntries(tools.map((t) => [t.name, t]));
const modelWithTools = model.bindTools(tools);

// Use the model
const response = await modelWithTools.invoke(
  "What is 5 + 3, and then multiply the result by 2?"
);

// Process tool calls
if (response.tool_calls) {
  for (const toolCall of response.tool_calls) {
    const tool = toolsByName[toolCall.name];
    const result = await tool.invoke(toolCall.args);
    console.log(`${toolCall.name}: ${result}`);
  }
}
```

---

## Complete Examples

### Translation Chain

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

async function createTranslationChain() {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY environment variable is required");
  }

  const model = new ChatOpenAI({ model: "gpt-4o-mini" });

  const prompt = ChatPromptTemplate.fromMessages([
    [
      "system",
      "You are a professional translator. Translate the following text from {source_lang} to {target_lang}. Only output the translation, nothing else.",
    ],
    ["human", "{text}"],
  ]);

  const chain = prompt.pipe(model).pipe(new StringOutputParser());

  // Single translation
  const result = await chain.invoke({
    source_lang: "English",
    target_lang: "Spanish",
    text: "Hello, how are you today?",
  });

  console.log(result);
  // "Hola, como estas hoy?"

  // Batch translation
  const batchResults = await chain.batch([
    { source_lang: "English", target_lang: "French", text: "Good morning" },
    { source_lang: "English", target_lang: "German", text: "Good night" },
  ]);

  console.log(batchResults);
}

createTranslationChain();
```

### Streaming Chat with Memory

```typescript
import * as readline from "readline";
import { ChatOpenAI } from "@langchain/openai";
import { HumanMessage, AIMessage, SystemMessage, BaseMessage } from "@langchain/core/messages";

async function runStreamingChat() {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY environment variable is required");
  }

  const model = new ChatOpenAI({
    model: "gpt-4o-mini",
    streaming: true,
  });

  const messages: BaseMessage[] = [
    new SystemMessage("You are a helpful, friendly assistant."),
  ];

  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });

  console.log("Chat started (with streaming). Type 'quit' to exit.\n");

  const askQuestion = () => {
    rl.question("You: ", async (userInput) => {
      const trimmedInput = userInput.trim();

      if (trimmedInput.toLowerCase() === "quit") {
        console.log("Goodbye!");
        rl.close();
        return;
      }

      if (!trimmedInput) {
        askQuestion();
        return;
      }

      messages.push(new HumanMessage(trimmedInput));

      process.stdout.write("Assistant: ");

      try {
        const stream = await model.stream(messages);
        let fullResponse = "";

        for await (const chunk of stream) {
          const content = chunk.content as string;
          process.stdout.write(content);
          fullResponse += content;
        }

        console.log("\n");

        // Add complete response to history
        messages.push(new AIMessage(fullResponse));
      } catch (error) {
        console.error("\nError:", error);
      }

      askQuestion();
    });
  };

  askQuestion();
}

runStreamingChat();
```

### Data Extraction with Structured Output

```typescript
import * as z from "zod";
import { ChatOpenAI } from "@langchain/openai";

async function extractContacts() {
  if (!process.env.OPENAI_API_KEY) {
    throw new Error("OPENAI_API_KEY environment variable is required");
  }

  // Define the schema
  const ContactInfo = z.object({
    name: z.string().describe("Full name of the person"),
    email: z.string().nullable().describe("Email address if found"),
    phone: z.string().nullable().describe("Phone number if found"),
    company: z.string().nullable().describe("Company name if found"),
  });

  const ExtractedContacts = z.object({
    contacts: z.array(ContactInfo).describe("All contacts found in the text"),
  });

  // Initialize model with structure
  const model = new ChatOpenAI({ model: "gpt-4o-mini" });
  const extractor = model.withStructuredOutput(ExtractedContacts);

  // Extract from unstructured text
  const text = `
Meeting notes from yesterday:
- John Smith (john.smith@acme.com, 555-1234) from Acme Corp will handle the backend.
- Contact Sarah Johnson at TechStart for the frontend. Her email is sarah@techstart.io
- Bob Williams mentioned his new number is 555-5678
`;

  const result = await extractor.invoke(
    `Extract all contact information from this text:\n\n${text}`
  );

  for (const contact of result.contacts) {
    console.log(`Name: ${contact.name}`);
    console.log(`  Email: ${contact.email}`);
    console.log(`  Phone: ${contact.phone}`);
    console.log(`  Company: ${contact.company}`);
    console.log();
  }
}

extractContacts();
```

---

## Best Practices

### 1. Environment Configuration

```typescript
// Never hardcode API keys
// Use environment variables and validate them

function getRequiredEnv(name: string): string {
  const value = process.env[name];
  if (!value) {
    throw new Error(`${name} environment variable is required`);
  }
  return value;
}

const apiKey = getRequiredEnv("OPENAI_API_KEY");
```

### 2. Error Handling

```typescript
import { ChatOpenAI } from "@langchain/openai";

async function safeInvoke(prompt: string): Promise<string> {
  const model = new ChatOpenAI({
    model: "gpt-4o-mini",
    maxRetries: 3,
    timeout: 30000,
  });

  try {
    const response = await model.invoke(prompt);
    return response.content as string;
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(`Failed to communicate with LLM: ${error.message}`);
    }
    throw error;
  }
}
```

### 3. Type Safety with Zod

```typescript
import * as z from "zod";

// Define schemas for all structured outputs
const ResponseSchema = z.object({
  answer: z.string(),
  confidence: z.number().min(0).max(1),
  sources: z.array(z.string()).optional(),
});

type Response = z.infer<typeof ResponseSchema>;

// Use with withStructuredOutput for type-safe responses
const model = new ChatOpenAI({ model: "gpt-4o-mini" });
const typedModel = model.withStructuredOutput(ResponseSchema);

const result: Response = await typedModel.invoke("What is TypeScript?");
```

### 4. Reusable Chain Patterns

```typescript
import { ChatOpenAI } from "@langchain/openai";
import { ChatPromptTemplate } from "@langchain/core/prompts";
import { StringOutputParser } from "@langchain/core/output_parsers";

function createSummarizationChain(modelName: string = "gpt-4o-mini") {
  const prompt = ChatPromptTemplate.fromMessages([
    [
      "system",
      "You are a skilled summarizer. Summarize the following text in {style} style.",
    ],
    ["human", "{text}"],
  ]);

  const model = new ChatOpenAI({ model: modelName });

  return prompt.pipe(model).pipe(new StringOutputParser());
}

// Use it
const summarizer = createSummarizationChain();
const summary = await summarizer.invoke({
  style: "bullet points",
  text: "Long article text here...",
});
```

### 5. Streaming for Better UX

```typescript
// Always use streaming for long responses to improve user experience
const model = new ChatOpenAI({
  model: "gpt-4o-mini",
  streaming: true,
});

// Stream to console or frontend
for await (const chunk of await model.stream("Write a detailed explanation")) {
  // Send chunk to frontend or display immediately
  process.stdout.write(chunk.content as string);
}
```

---

## Summary

This guide covered the essential LangChain.js capabilities for TypeScript:

| Feature | Description |
|---------|-------------|
| `initChatModel()` | Unified model initialization for any provider |
| Message Classes | `SystemMessage`, `HumanMessage`, `AIMessage` for typed conversations |
| `invoke()`, `stream()` | Core methods for model interaction |
| `ChatPromptTemplate` | Reusable templates with variable substitution |
| `.pipe()` | Chain components for complex workflows |
| `withStructuredOutput()` | Get type-safe Zod-validated responses |
| `tool()` | Define tools with Zod schemas |
| `bindTools()` | Attach tools to models |

For more advanced stateful agents and workflows, see the LangGraph.js documentation.
