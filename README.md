# Szkolenie – RAG, Langgraph i systemy agentowe

Informacje i materiały: https://edu.palej.dev/r/2026-06-09



## Instrukcja przygotowania środowiska

```bash
cp .env.example .env  # proszę wpisać API KEY to pliku .env
uv run test_environment.py
```



## Agenda

**Dzień 1**

1.  Omówienie środowiska i narzędzi
    - JupyterLab
    - Manager pakietów uv
    - API OpenAI / OpenRouter
    - Środowisko Langchain
    - Langgraph
    - Wektorowa baza danych Qdrant

2.  Omówienie workflow tworzenia systemu RAG
    - Wczytanie danych i podział na chunki
    - Embeddingi za pomocą modeli z Huggingface
    - Zapis embeddingów do bazy wektorowej
    - Retrieval semantyczny
    - Hybrid search - łączenie wyszukiwania dense i sparse
    - Filtrowanie payloadu podczas retrievalu
    - Reranking
    - Generowanie odpowiedzi przez LLM w oparciu o pozyskany kontekst
    - Stworzenie prototypu prostego RAGa
    - Wersja demo z interfejsem frontendowym dostępna pod adresem https://rag.palej.dev

3. Ewaluacja RAGa
    - Wprowadzenie do metryk ewaluujących systemy RAG
    - Biblioteka DeepEval i jej metryki ewaluacji RAGa
    - Biblioteka Ragas i jej metryki ewaluacji RAGa

4. Zaawansowany projekt RAG
    - Demo projektu: https://biblia.palej.dev
    - Opis projektu: asystent do pomocy analizy tekstu Biblii w oparciu o kontekst z tekstu źródłowego
    - Założenia projektu: generowanie zapytań do bazy wektorowej przez asystenta AI na podstawie oryginalnego pytania użytkownika, możliwość konfiguracji poziomu złożoności analizy
    - Implementacja prototypu w notebooku


**Dzień 2**
    
1. Wprowadzenie do LangGraph
    - Grafy przepływu w Langgraph
    - Reprezentacja stanu w grafie
    - Budowa i konfiguracja pipeline'u
    - Implementacja prostego grafu przepływu

2. Stworzenie pipeline'u  dla systemu RAG
    - Implementacja pipeline'u z wykorzystaniem Langgraph

3. Agenci AI oraz serwer MCP
    - Serwer MCP - czym jest i z czego się składa (zasoby, prompty, narzędzia)
    - Klient dla serwera MCP
    - Wprowadzenie do Pydantic AI - tworzymy prostego agenta konsumującego serwer MCP
    - Web scraping portalu z ogłoszeniami pracy i zamiana scrapera na narzędzia dla agenta
    - Agent do autonomicznego scrapowania ofert pracy i doboru najlepszej oferty na podstawie CV oraz oczekiwań kandydata
    
      ​	
    
