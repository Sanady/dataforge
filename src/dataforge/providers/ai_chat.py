"""AI Chat provider — assembles realistic conversation turns.

This is a **compound** provider (``_needs_forge = True``) that
delegates to ``ai_prompt`` and ``llm`` providers to assemble
realistic chat messages with role, model, content, and token usage.

Individual string fields are exposed in ``_field_map`` for Schema
compatibility.  The compound ``chat_message()`` method returns a
``dict`` and is available only via direct API use.
"""

from typing import TYPE_CHECKING, Literal, overload

from dataforge.backend import RandomEngine
from dataforge.providers.base import BaseProvider

if TYPE_CHECKING:
    from dataforge.core import DataForge

# Module-level constants — zero per-call allocation
_ROLES: tuple[str, ...] = (
    "system",
    "user",
    "assistant",
    "tool",
)

_CHAT_ROLES_WEIGHTED: tuple[tuple[str, int], ...] = (
    ("user", 40),
    ("assistant", 40),
    ("system", 15),
    ("tool", 5),
)
_CHAT_ROLE_VALUES: tuple[str, ...] = tuple(r for r, _ in _CHAT_ROLES_WEIGHTED)
_CHAT_ROLE_WEIGHTS: tuple[int, ...] = tuple(w for _, w in _CHAT_ROLES_WEIGHTED)


class AiChatProvider(BaseProvider):
    """Generates fake AI chat data — messages, roles, conversations.

    Delegates to ``ai_prompt`` and ``llm`` providers for content
    and metadata generation.

    Parameters
    ----------
    engine : RandomEngine
        The shared random engine instance.
    forge : DataForge
        The parent DataForge instance for cross-provider access.
    """

    __slots__ = ("_forge",)

    _provider_name = "ai_chat"
    _locale_modules: tuple[str, ...] = ()
    _needs_forge: bool = True
    _field_map: dict[str, str] = {
        "chat_role": "chat_role",
        "chat_model": "chat_model",
        "chat_content": "chat_content",
        "chat_tokens": "chat_tokens",
        "chat_finish_reason": "chat_finish_reason",
    }

    def __init__(self, engine: RandomEngine, forge: "DataForge") -> None:
        super().__init__(engine)
        self._forge = forge

    # ------------------------------------------------------------------
    # Individual field methods (for _field_map / Schema compatibility)
    # ------------------------------------------------------------------

    @overload
    def chat_role(self) -> str: ...
    @overload
    def chat_role(self, count: Literal[1]) -> str: ...
    @overload
    def chat_role(self, count: int) -> str | list[str]: ...
    def chat_role(self, count: int = 1) -> str | list[str]:
        """Generate a chat message role (user, assistant, system, tool)."""
        if count == 1:
            return self._engine.weighted_choice(_CHAT_ROLE_VALUES, _CHAT_ROLE_WEIGHTS)
        return self._engine.weighted_choices(
            _CHAT_ROLE_VALUES, _CHAT_ROLE_WEIGHTS, count
        )

    @overload
    def chat_model(self) -> str: ...
    @overload
    def chat_model(self, count: Literal[1]) -> str: ...
    @overload
    def chat_model(self, count: int) -> str | list[str]: ...
    def chat_model(self, count: int = 1) -> str | list[str]:
        """Generate a model name for the chat (delegates to llm.model_name)."""
        return self._forge.llm.model_name(count)

    @overload
    def chat_content(self) -> str: ...
    @overload
    def chat_content(self, count: Literal[1]) -> str: ...
    @overload
    def chat_content(self, count: int) -> str | list[str]: ...
    def chat_content(self, count: int = 1) -> str | list[str]:
        """Generate chat message content (delegates to ai_prompt.user_prompt)."""
        return self._forge.ai_prompt.user_prompt(count)

    @overload
    def chat_tokens(self) -> str: ...
    @overload
    def chat_tokens(self, count: Literal[1]) -> str: ...
    @overload
    def chat_tokens(self, count: int) -> str | list[str]: ...
    def chat_tokens(self, count: int = 1) -> str | list[str]:
        """Generate a token count for the message (delegates to llm.token_count)."""
        return self._forge.llm.token_count(count)

    @overload
    def chat_finish_reason(self) -> str: ...
    @overload
    def chat_finish_reason(self, count: Literal[1]) -> str: ...
    @overload
    def chat_finish_reason(self, count: int) -> str | list[str]: ...
    def chat_finish_reason(self, count: int = 1) -> str | list[str]:
        """Generate a finish reason (delegates to llm.finish_reason)."""
        return self._forge.llm.finish_reason(count)

    # ------------------------------------------------------------------
    # Compound message method (direct API only, not in _field_map)
    # ------------------------------------------------------------------

    def chat_message(self, count: int = 1) -> dict[str, str] | list[dict[str, str]]:
        """Generate a realistic chat message with role, model, content, tokens.

        Returns a dict with keys: ``role``, ``model``, ``content``,
        ``tokens``, ``finish_reason``.

        Parameters
        ----------
        count : int
            Number of messages to generate.

        Returns
        -------
        dict[str, str] or list[dict[str, str]]
        """

        def _one_message() -> dict[str, str]:
            role = self._engine.weighted_choice(_CHAT_ROLE_VALUES, _CHAT_ROLE_WEIGHTS)
            model = self._forge.llm.model_name()
            # Pick content based on role for realism
            if role == "system":
                content = self._forge.ai_prompt.system_prompt()
            elif role == "user":
                content = self._forge.ai_prompt.user_prompt()
            else:
                # assistant or tool — use a user prompt as stand-in
                content = self._forge.ai_prompt.user_prompt()
            tokens = self._forge.llm.token_count()
            finish = self._forge.llm.finish_reason()
            return {
                "role": role,
                "model": model,
                "content": content,
                "tokens": tokens,
                "finish_reason": finish,
            }

        if count == 1:
            return _one_message()
        return [_one_message() for _ in range(count)]
