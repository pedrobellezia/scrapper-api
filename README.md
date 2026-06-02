# Scrapper API

API FastAPI para web scraping de dados públicos brasileiros com resolução automática de CAPTCHA.

## ✨ Características

- 🌐 **Web Scraping**: Coleta de dados de portais públicos (Trabalhista, FGTS, Estadual, Municipal)
- 🔐 **Autenticação**: Segurança via Bearer Token
- 🤖 **CAPTCHA Automático**: Resolução via 2Captcha
- 📄 **Geração de PDF**: Conversão de dados coletados em PDF
- 📊 **Logging Estruturado**: Logs em JSON para análise
- 🛡️ **CORS Configurável**: Origem segura de requisições
- ⚡ **Concorrência Limitada**: Controle de requisições simultâneas
- ✅ **Validação de Dados**: Schemas Pydantic robustos

## 📋 Pré-requisitos

- Python 3.11+
- pip ou uv (gerenciador de pacotes)
- Chave de API 2Captcha

## 🚀 Instalação

### 1. Clone o repositório
```bash
git clone <repository-url>
cd scrapper-api
```

### 2. Configure variáveis de ambiente
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

Ou com `uv`:
```bash
uv pip install -r requirements.txt
```

### 4. Instale os browsers do Playwright
```bash
playwright install chromium
```

## 📝 Configuração de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```env
# Autenticação
SECRET_KEY=sua_chave_secreta_super_segura

# 2Captcha API
CAPTCHA_API_KEY=sua_chave_2captcha

# Playwright
HEADLESS=False  # True para produção

# CORS (domínios permitidos)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Concorrência (máximo de requisições simultâneas)
MAX_CONCURRENT_BROWSERS=3
```

## 🏃 Iniciando a Aplicação

### Desenvolvimento (com reload)
```bash
python -m uvicorn app.app:app --host 0.0.0.0 --port 5049 --reload
```

### Produção (sem reload)
```bash
python -m uvicorn app.app:app --host 0.0.0.0 --port 5049
```

### Com Docker
```bash
docker-compose up -d
```

## 📡 Endpoints

### 1. Trabalhista
Coleta dados de processos trabalhistas.

```bash
curl -X POST http://localhost:5049/trabalhista \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "12345678000195"}' \
  --output resultado.pdf
```

### 2. FGTS
Coleta dados do FGTS.

```bash
curl -X POST http://localhost:5049/fgts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "12345678000195"}' \
  --output resultado.pdf
```

### 3. Estadual
Coleta dados estaduais.

```bash
curl -X POST http://localhost:5049/estadual \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "12345678000195", "uf": "SP"}' \
  --output resultado.pdf
```

### 4. Municipal
Coleta dados municipais.

```bash
curl -X POST http://localhost:5049/municipal \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"cnpj": "12345678000195", "uf": "SP", "municipio": "Sao Paulo"}' \
  --output resultado.pdf
```

### 5. Logs
Recupera histórico de logs com filtros.

```bash
curl -X POST http://localhost:5049/logs \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_cnd": ["trabalhista"],
    "cnpj": ["12345678000195"],
    "level": ["ERROR"],
    "init_date": "01-01-2024",
    "end_date": "31-12-2024"
  }'
```

## 🔐 Autenticação

Todos os endpoints (exceto GET) requerem Bearer Token no header:

```
Authorization: Bearer YOUR_SECRET_KEY
```

## 🏗️ Estrutura do Projeto

```
scrapper-api/
├── app/
│   ├── config/           # Configurações e setup
│   ├── exceptions/       # Exceções customizadas
│   ├── router/          # Endpoints
│   ├── services/        # Lógica de negócio
│   ├── schemas/         # Validação Pydantic
│   └── utils/           # Utilitários
├── logs/                # Logs em JSONL
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

## 📝 Logs

Os logs são salvos em `/logs` com a estrutura:
- Nome: `YYYY-MM-DD.jsonl` (um arquivo por dia)
- Formato: JSON Lines
- Níveis: INFO, WARNING, ERROR

## 🐛 Tratamento de Erros

A API retorna respostas estruturadas:

```json
{
  "detail": "Mensagem de erro",
  "error": "error_code",
  "cnd_type": "tipo_condicionador"
}
```

Códigos de erro:
- `request_validation_error` (422): Validação de payload
- `scrap_error` (502): Erro ao fazer scraping
- `captcha_error` (502): Erro ao resolver CAPTCHA
- `internal_error` (500): Erro interno

## 🔧 Desenvolvimento

### Adicionar novo endpoint

1. Crie o schema em `app/schemas/requests.py`
2. Crie o serviço em `app/services/novo_servico.py`
3. Crie o router em `app/router/novo_servico.py`
4. Registre em `app/config/server_configs.py`

### Executar testes
```bash
pytest
```

## 🚢 Deploy

### Docker Compose (Recomendado)
```bash
docker-compose up -d
```

### Produção com Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.app:app
```

## 📚 Dependências Principais

- **fastapi**: Framework web
- **playwright**: Web scraping
- **pydantic**: Validação de dados
- **2captcha-python**: Resolução de CAPTCHA
- **reportlab**: Geração de PDF
- **rich**: Logging com formatação
- **python-dotenv**: Variáveis de ambiente

## 📄 Licença

[Adicione sua licença aqui]

## 👨‍💼 Autor

[Seu Nome/Organização]

## 🤝 Contribuindo

[Instruções para contribuições]

