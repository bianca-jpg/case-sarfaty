import os
import json
import re
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from groq import Groq
from dotenv import load_dotenv

backend_dir = Path(__file__).resolve().parent
project_root = backend_dir.parent

load_dotenv(dotenv_path=backend_dir / ".env", override=False)
load_dotenv(dotenv_path=project_root / ".env", override=False)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

app = FastAPI(title="Sarfaty AI Triage API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir o Frontend estático (pasta `frontend/`) na raiz
frontend_dir = project_root / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir), html=True), name="static")


@app.get("/")
async def serve_index():
    index_path = frontend_dir / "index.html"
    return FileResponse(index_path)

class MensagemEntrada(BaseModel):
    id: int
    assunto: str
    mensagem: str

class ClassificacaoSaida(BaseModel):
    id: int
    tipo_solicitacao: str
    empresa: Optional[str] = None
    cnpj: Optional[str] = None
    documentos_identificados: List[str] = []
    area_sugerida: str
    proxima_acao: str
    confianca: str = Field(pattern="^(alto|médio|baixo)$")
    justificativa: str

@app.post("/api/classificar", response_model=ClassificacaoSaida)
async def classificar_mensagem(entrada: MensagemEntrada):
    mensagens = [
        {
            "role": "system",
            "content": """Você é um assistente de triagem financeira. Analise a mensagem e retorne EXCLUSIVAMENTE um objeto JSON.
            
            CONTEXTO E REGRAS DE NEGÓCIO (MAPA DE ÁREAS):
            Para preencher a "area_sugerida", você deve OBRIGATORIAMENTE seguir este mapeamento:
            - Se for "interesse_em_credito_pj" -> Encaminhar para a área: "Comercial"
            - Se for "atualizacao_cadastral" ou "envio_de_documentacao" -> Encaminhar para a área: "Operações e Cadastro"
            - Se for "solicitacao_segunda_via" -> Encaminhar para a área: "Atendimento ao Cliente"
            - Se for "duvida_operacao" ou "pendencia_informacao" -> Encaminhar para a área: "Especialistas em Produtos"
            - Se for suporte técnico, notebook ou "fora_do_escopo" -> Encaminhar para a área: "TI / Helpdesk"

            Estrutura OBRIGATÓRIA do JSON:
            {
                "tipo_solicitacao": "escolha entre: interesse_em_credito_pj, atualizacao_cadastral, envio_de_documentacao, solicitacao_segunda_via, duvida_operacao, pendencia_informacao, fora_do_escopo",
                "empresa": "nome da empresa ou null",
                "cnpj": "cnpj ou null",
                "documentos_identificados": ["lista", "de", "documentos"],
                "area_sugerida": "área sugerida seguindo estritamente o MAPA DE ÁREAS acima",
                "proxima_acao": "ação a ser tomada pelo setor",
                "confianca": "alto", "médio" ou "baixo",
                "justificativa": "1 a 2 frases explicando o motivo da classificação"
            }"""
        },
        {
            "role": "user",
            "content": f"Assunto: {entrada.assunto}\nMensagem: {entrada.mensagem}"
        }
    ]

    if not client:
        raise HTTPException(
            status_code=500,
            detail="GROQ_API_KEY não configurada. Copie backend/.env.example para backend/.env e defina sua chave antes de usar a classificação.",
        )

    try:
        # Solicita à Groq um retorno estritamente em JSON conforme schema
        json_schema = {
            "type": "object",
            "properties": {
                "tipo_solicitacao": {"type": "string"},
                "empresa": {"type": ["string", "null"]},
                "cnpj": {"type": ["string", "null"]},
                "documentos_identificados": {"type": "array", "items": {"type": "string"}},
                "area_sugerida": {"type": "string"},
                "proxima_acao": {"type": "string"},
                "confianca": {"type": "string", "enum": ["alto", "médio", "baixo"]},
                "justificativa": {"type": "string"}
            },
            "required": ["tipo_solicitacao", "area_sugerida", "proxima_acao", "confianca", "justificativa"]
        }

        try:
            chat_completion = client.chat.completions.create(
                messages=mensagens,
                model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                temperature=0.1,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "triagem_schema",
                        "json_schema": json_schema,
                    },
                },
            )
        except Exception as e:
            err = str(e)
            if "does not support response format" in err or "response_format" in err:
                # Model doesn't support json_schema — retry with json_object
                chat_completion = client.chat.completions.create(
                    messages=mensagens,
                    model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )
            else:
                raise

        # Extrai o texto retornado e tenta carregar como JSON
        texto_bruto = getattr(chat_completion.choices[0].message, 'content', str(chat_completion))
        try:
            resultado_json = json.loads(texto_bruto)
        except json.JSONDecodeError:
            # Fallback: tenta extrair o primeiro objeto JSON presente no texto
            match = re.search(r"\{.*\}", texto_bruto, flags=re.DOTALL)
            if match:
                try:
                    resultado_json = json.loads(match.group(0))
                except Exception:
                    raise HTTPException(status_code=500, detail=f"IA retornou JSON inválido: {texto_bruto}")
            else:
                raise HTTPException(status_code=500, detail=f"IA retornou resposta inesperada: {texto_bruto}")
        resultado_json["id"] = entrada.id
        
        return ClassificacaoSaida(**resultado_json)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar com IA: {str(e)}")

@app.get("/api/exemplos")
async def listar_exemplos():
    try:
        base = Path(__file__).resolve().parent
        entradas_path = base / "entradas.json"
        if not entradas_path.exists():
            entradas_path = project_root / "backend" / "entradas.json"

        with entradas_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []