from langchain_ollama import ChatOllama

llm = ChatOllama(model="llama3.1:8b", base_url="http://localhost:11434")
response = llm.invoke("Say 'Ollama is connected' and nothing else.")
print(response.content)