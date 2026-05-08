"""Context engine — manages conversation context window and compression.

When the conversation approaches the model's token limit, the context engine
compresses older messages by summarizing them, preserving key information
while freeing up space for new interactions.

Inspired by hermes-agent's ContextEngine / ContextCompressor pattern.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Approximate chars per token (varies by language; CJK ≈ 1.5, EN ≈ 4)
CHARS_PER_TOKEN = 2.5


def estimate_tokens(text: str) -> int:
    """Rough token count estimate."""
    return max(1, int(len(text) / CHARS_PER_TOKEN))


def estimate_messages_tokens(messages: List[Dict[str, str]]) -> int:
    """Estimate total tokens in a message list."""
    total = 0
    for msg in messages:
        content = msg.get("content", "")
        total += estimate_tokens(content) + 4  # role overhead
    return total


class ContextEngine:
    """Manages conversation context within a token budget.

    Strategy:
    1. System prompt is always preserved (pinned).
    2. Recent N messages are always preserved (tail window).
    3. Older messages are compressed: summarized into a single message.
    """

    def __init__(
        self,
        max_context_tokens: int = 8000,
        tail_window: int = 6,
        compression_ratio: float = 0.3,
    ):
        self.max_context_tokens = max_context_tokens
        self.tail_window = tail_window
        self.compression_ratio = compression_ratio

    def fit(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        """Trim/compress messages to fit within the token budget.

        Returns a new message list that fits within max_context_tokens.
        """
        if not messages:
            return messages

        total_tokens = estimate_messages_tokens(messages)
        if system_prompt:
            total_tokens += estimate_tokens(system_prompt) + 4

        # If within budget, return as-is
        if total_tokens <= self.max_context_tokens:
            return messages

        # Split into: [old messages] + [tail window]
        if len(messages) <= self.tail_window:
            # All messages are "recent" — just truncate content
            return self._truncate_messages(messages, self.max_context_tokens)

        old_messages = messages[:-self.tail_window]
        recent_messages = messages[-self.tail_window:]

        # Compress old messages into a summary
        budget_for_old = max(
            200,
            self.max_context_tokens
            - estimate_messages_tokens(recent_messages)
            - (estimate_tokens(system_prompt) + 4 if system_prompt else 0)
            - 50,  # buffer
        )

        compressed = self._compress_messages(old_messages, budget_for_old)
        result = compressed + recent_messages

        # Final safety check
        final_tokens = estimate_messages_tokens(result)
        if final_tokens > self.max_context_tokens:
            result = self._truncate_messages(result, self.max_context_tokens)

        return result

    def _compress_messages(
        self, messages: List[Dict[str, str]], token_budget: int
    ) -> List[Dict[str, str]]:
        """Compress a list of messages into a single summary message."""
        if not messages:
            return []

        # Build a condensed representation
        parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if not content:
                continue
            # Keep first 200 chars of each message
            truncated = content[:200] + ("..." if len(content) > 200 else "")
            parts.append(f"[{role}]: {truncated}")

        summary_text = "[Earlier conversation summary]\n" + "\n".join(parts)

        # Truncate to budget
        max_chars = int(token_budget * CHARS_PER_TOKEN)
        if len(summary_text) > max_chars:
            summary_text = summary_text[:max_chars - 20] + "...[truncated]"

        return [{"role": "system", "content": summary_text}]

    def _truncate_messages(
        self, messages: List[Dict[str, str]], token_budget: int
    ) -> List[Dict[str, str]]:
        """Last resort: truncate individual messages to fit budget."""
        max_chars = int(token_budget * CHARS_PER_TOKEN)
        result = []
        used = 0
        for msg in messages:
            content = msg.get("content", "")
            remaining = max_chars - used
            if remaining <= 0:
                break
            if len(content) > remaining:
                content = content[:remaining - 10] + "...[truncated]"
            result.append({**msg, "content": content})
            used += len(content) + 4
        return result

    def inject_tool_results(
        self,
        messages: List[Dict[str, str]],
        tool_results: List[Dict[str, str]],
    ) -> List[Dict[str, str]]:
        """Append tool results to messages, respecting token budget."""
        combined = messages + tool_results
        return self.fit(combined)
