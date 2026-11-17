# Hugging Face Agents Course — Estudos e Prática

Repositório pessoal com anotações conceituais e implementações desenvolvidas durante o **[Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course)**, executando modelos locais via **Ollama (`qwen2.5:7b`)** (parece que tiraram a free tier da API do Hugging Face...).

---

## Estrutura do Repositório

```text
├── Unit 1 - Introduction to Agents/
│   ├── anotacoes.md             # Anotações conceituais (LLMs stateless, ReAct vs CoT, MCP, Reflection)
│   ├── dummy-agent-library.py   # Implementação manual do loop ReAct (parsing dinâmico de tools sem hardcode)
│   └── my_agent.py              # Agente construído com o framework smolagents + @tool + LiteLLMModel
├── .env.example                 # Exemplo de configuração de ambiente
└── README.md
```

---

## Unidades

### [Unit 1: Introduction to Agents](./Unit%201%20-%20Introduction%20to%20Agents/)
* **Anotações detalhadas:** [anotacoes.md](./Unit%201%20-%20Introduction%20to%20Agents/anotacoes.md)
  * Como LLMs operam por debaixo dos panos (*stateless* e *chat templates*).
  * Por que linguagens de programação são ideais para definição de *tools* (expressividade e reflexão com `inspect`).
  * Origem e padronização do **Model Context Protocol (MCP)**.
  * Comparativo estrutural: **Chain-of-Thought (CoT)** vs. **Reasoning + Acting (ReAct)**.
* **Prática:**
  * Execução local via **Ollama** (`qwen2.5:7b`) apontando para `http://127.0.0.1:11434/v1`.
  * Comparativo entre resolver o loop ReAct na mão com extração dinâmica de JSON vs. usar o framework de alto nível `smolagents`.

---

## Como Executar Localmente

### Pré-requisitos
1. [Ollama](https://ollama.com/) instalado com o modelo `qwen2.5:7b`:
   ```powershell
   ollama run qwen2.5:7b
   ```
2. Ambiente Python virtual configurado:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install smolagents huggingface_hub python-dotenv
   ```

### Executar os Scripts da Unit 1
```powershell
python "Unit 1 - Introduction to Agents\dummy-agent-library.py"
python "Unit 1 - Introduction to Agents\my_agent.py"
```
