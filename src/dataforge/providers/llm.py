"""LLM provider — model metadata, agents, RAG, moderation, usage/billing."""

from typing import Literal, overload

from dataforge.providers.base import BaseProvider

# ---------------------------------------------------------------------------
# Module-level immutable tuples — zero per-call allocation
# ---------------------------------------------------------------------------

# --- LLM metadata ---

_MODEL_NAMES: tuple[str, ...] = (
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-3.5-turbo",
    "claude-3.5-sonnet",
    "claude-3.5-haiku",
    "claude-3-opus",
    "claude-3-sonnet",
    "claude-3-haiku",
    "gemini-2.0-flash",
    "gemini-1.5-pro",
    "gemini-1.5-flash",
    "llama-3.1-405b",
    "llama-3.1-70b",
    "llama-3.1-8b",
    "mistral-large",
    "mistral-medium",
    "mistral-small",
    "mixtral-8x22b",
    "mixtral-8x7b",
    "command-r-plus",
    "command-r",
    "deepseek-v3",
    "deepseek-r1",
    "qwen-2.5-72b",
    "phi-4",
    "yi-large",
    "dbrx-instruct",
    "jamba-1.5-large",
)

_PROVIDER_NAMES: tuple[str, ...] = (
    "OpenAI",
    "Anthropic",
    "Google",
    "Meta",
    "Mistral",
    "Cohere",
    "DeepSeek",
    "Alibaba Cloud",
    "Microsoft",
    "AI21 Labs",
    "Databricks",
    "Amazon Bedrock",
    "Azure OpenAI",
    "Hugging Face",
    "Replicate",
    "Together AI",
    "Groq",
    "Fireworks AI",
    "Perplexity",
    "Anyscale",
)

_FINISH_REASONS: tuple[str, ...] = (
    "stop",
    "length",
    "content_filter",
    "tool_calls",
    "end_turn",
    "max_tokens",
    "stop_sequence",
    "function_call",
)

_STOP_SEQUENCES: tuple[str, ...] = (
    "<|endoftext|>",
    "<|end|>",
    "</s>",
    "[DONE]",
    "\\n\\n",
    "<stop>",
    "###",
    "---",
    "Human:",
    "User:",
)

# API key prefixes — realistic per-provider patterns
_API_KEY_PREFIXES: tuple[str, ...] = (
    "sk-",
    "sk-proj-",
    "sk-ant-api03-",
    "AI",
    "gsk_",
    "xai-",
    "pplx-",
    "r8_",
    "hf_",
    "co-",
)

# --- AI Agent / Tool use ---

_TOOL_NAMES: tuple[str, ...] = (
    "web_search",
    "code_interpreter",
    "file_reader",
    "calculator",
    "image_generator",
    "text_to_speech",
    "database_query",
    "api_caller",
    "email_sender",
    "calendar_manager",
    "document_parser",
    "translation_tool",
    "weather_lookup",
    "stock_price",
    "url_fetcher",
    "json_validator",
    "csv_parser",
    "pdf_extractor",
    "screenshot_tool",
    "clipboard_manager",
)

_AGENT_NAMES: tuple[str, ...] = (
    "ResearchAgent",
    "CodingAssistant",
    "DataAnalyzer",
    "ContentWriter",
    "TaskPlanner",
    "DebugHelper",
    "ReviewBot",
    "SummaryAgent",
    "TranslatorAgent",
    "MonitoringAgent",
    "DeploymentAgent",
    "TestRunner",
    "DocumentAgent",
    "SchedulerBot",
    "SecurityScanner",
    "PerformanceAgent",
    "MigrationHelper",
    "ComplianceChecker",
    "IncidentResponder",
    "OnboardingBot",
)

_MCP_SERVER_NAMES: tuple[str, ...] = (
    "filesystem",
    "github",
    "slack",
    "postgres",
    "sqlite",
    "brave-search",
    "google-maps",
    "puppeteer",
    "memory",
    "sequential-thinking",
    "google-drive",
    "notion",
    "jira",
    "confluence",
    "aws",
    "kubernetes",
    "docker",
    "redis",
    "elasticsearch",
    "mongodb",
)

_CAPABILITIES: tuple[str, ...] = (
    "text-generation",
    "code-completion",
    "image-understanding",
    "tool-use",
    "function-calling",
    "structured-output",
    "streaming",
    "embeddings",
    "fine-tuning",
    "batch-processing",
    "vision",
    "audio-transcription",
    "text-to-speech",
    "retrieval-augmented-generation",
    "multi-turn-conversation",
    "json-mode",
    "system-prompts",
    "parallel-tool-calls",
    "citation-generation",
    "web-browsing",
)

# --- RAG / Embeddings ---

_EMBEDDING_MODELS: tuple[str, ...] = (
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
    "voyage-3",
    "voyage-3-lite",
    "voyage-code-3",
    "embed-english-v3.0",
    "embed-multilingual-v3.0",
    "nomic-embed-text-v1.5",
    "bge-large-en-v1.5",
    "bge-m3",
    "gte-large",
    "e5-large-v2",
    "jina-embeddings-v3",
    "mxbai-embed-large-v1",
    "all-MiniLM-L6-v2",
    "instructor-xl",
    "cohere-embed-english-v3",
    "titan-embed-text-v2",
    "gecko-embedding",
)

_VECTOR_DB_NAMES: tuple[str, ...] = (
    "Pinecone",
    "Weaviate",
    "Milvus",
    "Qdrant",
    "ChromaDB",
    "pgvector",
    "Elasticsearch",
    "Redis Vector",
    "LanceDB",
    "Vespa",
    "Zilliz Cloud",
    "Supabase Vector",
    "MongoDB Atlas Vector",
    "Azure AI Search",
    "Google Vertex AI",
    "OpenSearch",
    "Turbopuffer",
    "Marqo",
    "Deep Lake",
    "Vald",
)

_NAMESPACES: tuple[str, ...] = (
    "default",
    "production",
    "staging",
    "development",
    "documents",
    "knowledge-base",
    "user-content",
    "faq",
    "support-tickets",
    "product-catalog",
    "blog-posts",
    "code-snippets",
    "meeting-notes",
    "research-papers",
    "customer-data",
)

# --- Content moderation ---

_MODERATION_CATEGORIES: tuple[str, ...] = (
    "hate",
    "hate/threatening",
    "harassment",
    "harassment/threatening",
    "self-harm",
    "self-harm/intent",
    "self-harm/instructions",
    "sexual",
    "sexual/minors",
    "violence",
    "violence/graphic",
    "illicit",
    "illicit/violent",
)

_HARM_LABELS: tuple[str, ...] = (
    "safe",
    "low_risk",
    "medium_risk",
    "high_risk",
    "blocked",
    "flagged",
    "requires_review",
    "auto_approved",
    "escalated",
    "filtered",
)

# --- Usage / Billing ---

_RATE_LIMIT_NAMES: tuple[str, ...] = (
    "x-ratelimit-limit-requests",
    "x-ratelimit-limit-tokens",
    "x-ratelimit-remaining-requests",
    "x-ratelimit-remaining-tokens",
    "x-ratelimit-reset-requests",
    "x-ratelimit-reset-tokens",
    "retry-after",
    "x-request-id",
)

# Hex chars for API key / ID generation — avoids repeated string allocation
_HEX_CHARS: str = "0123456789abcdef"
_ALPHANUM: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


class LlmProvider(BaseProvider):
    """Generates fake LLM ecosystem data — models, agents, RAG, moderation, billing."""

    __slots__ = ()

    _provider_name = "llm"
    _locale_modules: tuple[str, ...] = ()
    _field_map: dict[str, str] = {
        # LLM metadata
        "model_name": "model_name",
        "llm_provider": "provider_name",
        "provider_name": "provider_name",
        "api_key": "api_key",
        "finish_reason": "finish_reason",
        "stop_sequence": "stop_sequence",
        # Agent / tool use
        "tool_name": "tool_name",
        "tool_call_id": "tool_call_id",
        "mcp_server_name": "mcp_server_name",
        "agent_name": "agent_name",
        "capability": "capability",
        # RAG / embeddings
        "embedding_model": "embedding_model",
        "vector_db_name": "vector_db_name",
        "chunk_id": "chunk_id",
        "similarity_score": "similarity_score",
        "namespace": "namespace",
        # Content moderation
        "moderation_category": "moderation_category",
        "moderation_score": "moderation_score",
        "harm_label": "harm_label",
        # Usage / billing
        "token_count": "token_count",
        "prompt_tokens": "prompt_tokens",
        "completion_tokens": "completion_tokens",
        "cost_estimate": "cost_estimate",
        "rate_limit_header": "rate_limit_header",
    }

    # ===================================================================
    # LLM metadata
    # ===================================================================

    @overload
    def model_name(self) -> str: ...
    @overload
    def model_name(self, count: Literal[1]) -> str: ...
    @overload
    def model_name(self, count: int) -> str | list[str]: ...
    def model_name(self, count: int = 1) -> str | list[str]:
        """Generate an LLM model name (e.g. gpt-4o, claude-3.5-sonnet)."""
        if count == 1:
            return self._engine.choice(_MODEL_NAMES)
        return self._engine.choices(_MODEL_NAMES, count)

    @overload
    def provider_name(self) -> str: ...
    @overload
    def provider_name(self, count: Literal[1]) -> str: ...
    @overload
    def provider_name(self, count: int) -> str | list[str]: ...
    def provider_name(self, count: int = 1) -> str | list[str]:
        """Generate an LLM provider name (e.g. OpenAI, Anthropic)."""
        if count == 1:
            return self._engine.choice(_PROVIDER_NAMES)
        return self._engine.choices(_PROVIDER_NAMES, count)

    def _one_api_key(self) -> str:
        prefix = self._engine.choice(_API_KEY_PREFIXES)
        # Generate 40 alphanumeric chars — realistic key length
        _ri = self._engine.random_int
        an = _ALPHANUM
        an_len = len(an)
        return prefix + "".join(an[_ri(0, an_len - 1)] for _ in range(40))

    @overload
    def api_key(self) -> str: ...
    @overload
    def api_key(self, count: Literal[1]) -> str: ...
    @overload
    def api_key(self, count: int) -> str | list[str]: ...
    def api_key(self, count: int = 1) -> str | list[str]:
        """Generate a realistic-looking API key."""
        if count == 1:
            return self._one_api_key()
        # Inlined batch with local binding
        _choice = self._engine.choice
        _ri = self._engine.random_int
        _prefixes = _API_KEY_PREFIXES
        an = _ALPHANUM
        an_len = len(an)
        result: list[str] = []
        for _ in range(count):
            prefix = _choice(_prefixes)
            result.append(prefix + "".join(an[_ri(0, an_len - 1)] for _j in range(40)))
        return result

    @overload
    def finish_reason(self) -> str: ...
    @overload
    def finish_reason(self, count: Literal[1]) -> str: ...
    @overload
    def finish_reason(self, count: int) -> str | list[str]: ...
    def finish_reason(self, count: int = 1) -> str | list[str]:
        """Generate an LLM finish reason (e.g. stop, length, tool_calls)."""
        if count == 1:
            return self._engine.choice(_FINISH_REASONS)
        return self._engine.choices(_FINISH_REASONS, count)

    @overload
    def stop_sequence(self) -> str: ...
    @overload
    def stop_sequence(self, count: Literal[1]) -> str: ...
    @overload
    def stop_sequence(self, count: int) -> str | list[str]: ...
    def stop_sequence(self, count: int = 1) -> str | list[str]:
        """Generate a stop sequence token."""
        if count == 1:
            return self._engine.choice(_STOP_SEQUENCES)
        return self._engine.choices(_STOP_SEQUENCES, count)

    # ===================================================================
    # AI Agent / Tool use
    # ===================================================================

    @overload
    def tool_name(self) -> str: ...
    @overload
    def tool_name(self, count: Literal[1]) -> str: ...
    @overload
    def tool_name(self, count: int) -> str | list[str]: ...
    def tool_name(self, count: int = 1) -> str | list[str]:
        """Generate a tool/function name for AI agents."""
        if count == 1:
            return self._engine.choice(_TOOL_NAMES)
        return self._engine.choices(_TOOL_NAMES, count)

    def _one_tool_call_id(self) -> str:
        # Format: call_XXXX... (24 alphanumeric chars) — matches OpenAI format
        _ri = self._engine.random_int
        an = _ALPHANUM
        an_len = len(an)
        return "call_" + "".join(an[_ri(0, an_len - 1)] for _ in range(24))

    @overload
    def tool_call_id(self) -> str: ...
    @overload
    def tool_call_id(self, count: Literal[1]) -> str: ...
    @overload
    def tool_call_id(self, count: int) -> str | list[str]: ...
    def tool_call_id(self, count: int = 1) -> str | list[str]:
        """Generate a tool call ID (e.g. call_abc123...)."""
        if count == 1:
            return self._one_tool_call_id()
        # Inlined batch with local binding
        _ri = self._engine.random_int
        an = _ALPHANUM
        an_len = len(an)
        return [
            "call_" + "".join(an[_ri(0, an_len - 1)] for _j in range(24))
            for _ in range(count)
        ]

    @overload
    def mcp_server_name(self) -> str: ...
    @overload
    def mcp_server_name(self, count: Literal[1]) -> str: ...
    @overload
    def mcp_server_name(self, count: int) -> str | list[str]: ...
    def mcp_server_name(self, count: int = 1) -> str | list[str]:
        """Generate an MCP server name (e.g. filesystem, github)."""
        if count == 1:
            return self._engine.choice(_MCP_SERVER_NAMES)
        return self._engine.choices(_MCP_SERVER_NAMES, count)

    @overload
    def agent_name(self) -> str: ...
    @overload
    def agent_name(self, count: Literal[1]) -> str: ...
    @overload
    def agent_name(self, count: int) -> str | list[str]: ...
    def agent_name(self, count: int = 1) -> str | list[str]:
        """Generate an AI agent name (e.g. ResearchAgent, CodingAssistant)."""
        if count == 1:
            return self._engine.choice(_AGENT_NAMES)
        return self._engine.choices(_AGENT_NAMES, count)

    @overload
    def capability(self) -> str: ...
    @overload
    def capability(self, count: Literal[1]) -> str: ...
    @overload
    def capability(self, count: int) -> str | list[str]: ...
    def capability(self, count: int = 1) -> str | list[str]:
        """Generate an LLM capability (e.g. tool-use, streaming, vision)."""
        if count == 1:
            return self._engine.choice(_CAPABILITIES)
        return self._engine.choices(_CAPABILITIES, count)

    # ===================================================================
    # RAG / Embeddings
    # ===================================================================

    @overload
    def embedding_model(self) -> str: ...
    @overload
    def embedding_model(self, count: Literal[1]) -> str: ...
    @overload
    def embedding_model(self, count: int) -> str | list[str]: ...
    def embedding_model(self, count: int = 1) -> str | list[str]:
        """Generate an embedding model name."""
        if count == 1:
            return self._engine.choice(_EMBEDDING_MODELS)
        return self._engine.choices(_EMBEDDING_MODELS, count)

    @overload
    def vector_db_name(self) -> str: ...
    @overload
    def vector_db_name(self, count: Literal[1]) -> str: ...
    @overload
    def vector_db_name(self, count: int) -> str | list[str]: ...
    def vector_db_name(self, count: int = 1) -> str | list[str]:
        """Generate a vector database name (e.g. Pinecone, ChromaDB)."""
        if count == 1:
            return self._engine.choice(_VECTOR_DB_NAMES)
        return self._engine.choices(_VECTOR_DB_NAMES, count)

    def _one_chunk_id(self) -> str:
        # Format: chunk_XXXXXXXX (8 hex chars)
        bits = self._engine.getrandbits(32)
        return f"chunk_{bits:08x}"

    @overload
    def chunk_id(self) -> str: ...
    @overload
    def chunk_id(self, count: Literal[1]) -> str: ...
    @overload
    def chunk_id(self, count: int) -> str | list[str]: ...
    def chunk_id(self, count: int = 1) -> str | list[str]:
        """Generate a document chunk ID (e.g. chunk_a1b2c3d4)."""
        if count == 1:
            return self._one_chunk_id()
        # Inlined batch with local binding
        _getrandbits = self._engine.getrandbits
        return [f"chunk_{_getrandbits(32):08x}" for _ in range(count)]

    def _one_similarity_score(self) -> str:
        # Score between 0.0 and 1.0 with 4 decimal places
        return f"{self._engine.random_int(0, 10000) / 10000.0:.4f}"

    @overload
    def similarity_score(self) -> str: ...
    @overload
    def similarity_score(self, count: Literal[1]) -> str: ...
    @overload
    def similarity_score(self, count: int) -> str | list[str]: ...
    def similarity_score(self, count: int = 1) -> str | list[str]:
        """Generate a similarity/relevance score (0.0000-1.0000)."""
        if count == 1:
            return self._one_similarity_score()
        # Inlined batch with local binding
        _ri = self._engine.random_int
        return [f"{_ri(0, 10000) / 10000.0:.4f}" for _ in range(count)]

    @overload
    def namespace(self) -> str: ...
    @overload
    def namespace(self, count: Literal[1]) -> str: ...
    @overload
    def namespace(self, count: int) -> str | list[str]: ...
    def namespace(self, count: int = 1) -> str | list[str]:
        """Generate a vector DB namespace name."""
        if count == 1:
            return self._engine.choice(_NAMESPACES)
        return self._engine.choices(_NAMESPACES, count)

    # ===================================================================
    # Content moderation
    # ===================================================================

    @overload
    def moderation_category(self) -> str: ...
    @overload
    def moderation_category(self, count: Literal[1]) -> str: ...
    @overload
    def moderation_category(self, count: int) -> str | list[str]: ...
    def moderation_category(self, count: int = 1) -> str | list[str]:
        """Generate a content moderation category."""
        if count == 1:
            return self._engine.choice(_MODERATION_CATEGORIES)
        return self._engine.choices(_MODERATION_CATEGORIES, count)

    def _one_moderation_score(self) -> str:
        # Score between 0.0000 and 1.0000
        return f"{self._engine.random_int(0, 10000) / 10000.0:.4f}"

    @overload
    def moderation_score(self) -> str: ...
    @overload
    def moderation_score(self, count: Literal[1]) -> str: ...
    @overload
    def moderation_score(self, count: int) -> str | list[str]: ...
    def moderation_score(self, count: int = 1) -> str | list[str]:
        """Generate a moderation score (0.0000-1.0000)."""
        if count == 1:
            return self._one_moderation_score()
        _ri = self._engine.random_int
        return [f"{_ri(0, 10000) / 10000.0:.4f}" for _ in range(count)]

    @overload
    def harm_label(self) -> str: ...
    @overload
    def harm_label(self, count: Literal[1]) -> str: ...
    @overload
    def harm_label(self, count: int) -> str | list[str]: ...
    def harm_label(self, count: int = 1) -> str | list[str]:
        """Generate a harm/safety label (e.g. safe, blocked, flagged)."""
        if count == 1:
            return self._engine.choice(_HARM_LABELS)
        return self._engine.choices(_HARM_LABELS, count)

    # ===================================================================
    # Usage / Billing
    # ===================================================================

    def _one_token_count(self) -> str:
        return str(self._engine.random_int(1, 16384))

    @overload
    def token_count(self) -> str: ...
    @overload
    def token_count(self, count: Literal[1]) -> str: ...
    @overload
    def token_count(self, count: int) -> str | list[str]: ...
    def token_count(self, count: int = 1) -> str | list[str]:
        """Generate a token count (1-16384)."""
        if count == 1:
            return self._one_token_count()
        _ri = self._engine.random_int
        return [str(_ri(1, 16384)) for _ in range(count)]

    def _one_prompt_tokens(self) -> str:
        return str(self._engine.random_int(10, 8192))

    @overload
    def prompt_tokens(self) -> str: ...
    @overload
    def prompt_tokens(self, count: Literal[1]) -> str: ...
    @overload
    def prompt_tokens(self, count: int) -> str | list[str]: ...
    def prompt_tokens(self, count: int = 1) -> str | list[str]:
        """Generate a prompt token count (10-8192)."""
        if count == 1:
            return self._one_prompt_tokens()
        _ri = self._engine.random_int
        return [str(_ri(10, 8192)) for _ in range(count)]

    def _one_completion_tokens(self) -> str:
        return str(self._engine.random_int(1, 4096))

    @overload
    def completion_tokens(self) -> str: ...
    @overload
    def completion_tokens(self, count: Literal[1]) -> str: ...
    @overload
    def completion_tokens(self, count: int) -> str | list[str]: ...
    def completion_tokens(self, count: int = 1) -> str | list[str]:
        """Generate a completion token count (1-4096)."""
        if count == 1:
            return self._one_completion_tokens()
        _ri = self._engine.random_int
        return [str(_ri(1, 4096)) for _ in range(count)]

    def _one_cost_estimate(self) -> str:
        # Cost in USD: $0.0001 to $9.9999
        cents = self._engine.random_int(1, 99999)
        return f"${cents / 10000.0:.4f}"

    @overload
    def cost_estimate(self) -> str: ...
    @overload
    def cost_estimate(self, count: Literal[1]) -> str: ...
    @overload
    def cost_estimate(self, count: int) -> str | list[str]: ...
    def cost_estimate(self, count: int = 1) -> str | list[str]:
        """Generate a cost estimate in USD (e.g. $0.0234)."""
        if count == 1:
            return self._one_cost_estimate()
        _ri = self._engine.random_int
        return [f"${_ri(1, 99999) / 10000.0:.4f}" for _ in range(count)]

    def _one_rate_limit_header(self) -> str:
        name = self._engine.choice(_RATE_LIMIT_NAMES)
        value = str(self._engine.random_int(0, 100000))
        return f"{name}: {value}"

    @overload
    def rate_limit_header(self) -> str: ...
    @overload
    def rate_limit_header(self, count: Literal[1]) -> str: ...
    @overload
    def rate_limit_header(self, count: int) -> str | list[str]: ...
    def rate_limit_header(self, count: int = 1) -> str | list[str]:
        """Generate a rate limit HTTP header (e.g. x-ratelimit-remaining-tokens: 4500)."""
        if count == 1:
            return self._one_rate_limit_header()
        # Inlined batch with local binding
        _choice = self._engine.choice
        _ri = self._engine.random_int
        _names = _RATE_LIMIT_NAMES
        return [f"{_choice(_names)}: {_ri(0, 100000)}" for _ in range(count)]
