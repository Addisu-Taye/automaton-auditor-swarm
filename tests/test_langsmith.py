import os
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Verify env vars
print("LANGCHAIN_TRACING_V2:", os.getenv("LANGCHAIN_TRACING_V2"))
print("LANGCHAIN_API_KEY:", os.getenv("LANGCHAIN_API_KEY")[:10] + "..." if os.getenv("LANGCHAIN_API_KEY") else "NOT SET")
print("LANGCHAIN_PROJECT:", os.getenv("LANGCHAIN_PROJECT"))

# Simple test chain
llm = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("Say hello to {name}")
chain = prompt | llm | StrOutputParser()

# Invoke (should create trace in LangSmith)
result = chain.invoke({"name": "LangSmith Test"})
print(f"Result: {result}")
print("Check https://smith.langchain.com for traces")