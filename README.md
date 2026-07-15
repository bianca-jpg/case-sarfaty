# Triagem Inteligente de Mensagens - Grupo Sarfaty

Esta é uma Prova de Conceito (POC) desenvolvida para o processo seletivo de Trainee de Tecnologia do Grupo Sarfaty. O objetivo é automatizar a triagem inicial de mensagens de clientes e áreas internas utilizando Inteligência Artificial, extraindo dados estruturados e sugerindo as próximas ações.

## Tecnologias utilizadas

- Backend: Python com FastAPI
- Inteligência Artificial: Groq + modelos LLM
- Frontend: HTML, CSS e JavaScript vanilla
- Infraestrutura: Docker e Docker Compose

## Requisitos

- Python 3.11+
- pip
- Docker e Docker Compose (opcional, para execução em container)

## Configuração

1. Clone este repositório.
2. Crie o arquivo de ambiente baseado no exemplo:
   `ash
   copy backend\.env.example backend\.env
   `
   Em sistemas Linux/macOS, use:
   `ash
   cp backend/.env.example backend/.env
   `
3. Edite o arquivo ackend/.env e informe sua chave da Groq:
   `env
   GROQ_API_KEY=sua_chave_groq_aqui
   GROQ_MODEL=llama-3.1-8b-instant
   `

## Execução local

Instale as dependências:

`ash
pip install -r requirements.txt
`

Inicie a aplicação:

`ash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
`

A aplicação ficará disponível em http://localhost:8000.

## Execução com Docker

Na raiz do projeto, execute:

`ash
docker compose -f infra/docker-compose.yml up --build
`

A aplicação ficará disponível em http://localhost:8000.

## Estrutura do repositório

- ackend/: API FastAPI e lógica de classificação
- rontend/: interface web estática
- infra/: arquivos de containerização
- equirements.txt: dependências do projeto
