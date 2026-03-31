import asyncio
import inspect
import json
import threading
from typing import Any, Dict, List, Optional, Tuple

from backend.shared.llm_endpoints import normalize_anthropic_base_url


class ClaudeClient:
    def __init__(self, api_key: str, api_endpoint: Optional[str] = None):
        self.api_key = (api_key or "").strip()
        self.api_endpoint = normalize_anthropic_base_url(api_endpoint or "") if api_endpoint else ""

        try:
            from anthropic import Anthropic
        except Exception as e:
            raise RuntimeError("anthropic package is required for claude provider") from e

        kwargs: Dict[str, Any] = {"api_key": self.api_key}
        if self.api_endpoint:
            try:
                sig = inspect.signature(Anthropic)
                if "base_url" in sig.parameters:
                    kwargs["base_url"] = self.api_endpoint
            except Exception:
                pass

        self._client = Anthropic(**kwargs)

    @staticmethod
    def openai_tools_to_anthropic(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for t in tools or []:
            if not isinstance(t, dict):
                continue
            if t.get("type") != "function":
                continue
            fn = t.get("function")
            if not isinstance(fn, dict):
                continue
            name = fn.get("name")
            if not name:
                continue
            out.append(
                {
                    "name": name,
                    "description": fn.get("description") or "",
                    "input_schema": fn.get("parameters") or {"type": "object", "properties": {}},
                }
            )
        return out

    @staticmethod
    def _coerce_openai_content_to_text(content: Any) -> str:
        if content is None:
            return ""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: List[str] = []
            for p in content:
                if isinstance(p, dict):
                    if p.get("type") == "text" and isinstance(p.get("text"), str):
                        parts.append(p.get("text") or "")
            return "".join(parts)
        return str(content)

    @classmethod
    def openai_messages_to_anthropic(cls, messages: List[Dict[str, Any]]) -> Tuple[str, List[Dict[str, Any]]]:
        system_parts: List[str] = []
        out: List[Dict[str, Any]] = []
        for m in messages or []:
            if not isinstance(m, dict):
                continue
            role = (m.get("role") or "").strip().lower()
            content_text = cls._coerce_openai_content_to_text(m.get("content"))
            if role == "system":
                if content_text:
                    system_parts.append(content_text)
                continue
            if role not in ("user", "assistant"):
                continue
            out.append({"role": role, "content": content_text})
        return ("\n\n".join([p for p in system_parts if p]), out)

    @staticmethod
    def _extract_text_tool_uses_usage(message: Any) -> Tuple[str, List[Dict[str, Any]], Optional[Dict[str, Any]]]:
        text_parts: List[str] = []
        tool_uses: List[Dict[str, Any]] = []

        content = getattr(message, "content", None)
        if isinstance(content, list):
            for block in content:
                btype = getattr(block, "type", None)
                if btype is None and isinstance(block, dict):
                    btype = block.get("type")
                if btype == "text":
                    txt = getattr(block, "text", None)
                    if txt is None and isinstance(block, dict):
                        txt = block.get("text")
                    if isinstance(txt, str) and txt:
                        text_parts.append(txt)
                if btype == "tool_use":
                    tid = getattr(block, "id", None)
                    name = getattr(block, "name", None)
                    inp = getattr(block, "input", None)
                    if isinstance(block, dict):
                        tid = block.get("id")
                        name = block.get("name")
                        inp = block.get("input")
                    if tid and name:
                        tool_uses.append({"id": tid, "name": name, "input": inp or {}})

        usage_obj = getattr(message, "usage", None)
        usage: Optional[Dict[str, Any]] = None
        if usage_obj is not None:
            input_tokens = getattr(usage_obj, "input_tokens", None)
            output_tokens = getattr(usage_obj, "output_tokens", None)
            if isinstance(usage_obj, dict):
                input_tokens = usage_obj.get("input_tokens")
                output_tokens = usage_obj.get("output_tokens")
            if input_tokens is not None or output_tokens is not None:
                try:
                    it = int(input_tokens or 0)
                    ot = int(output_tokens or 0)
                    usage = {"prompt_tokens": it, "completion_tokens": ot, "total_tokens": it + ot}
                except Exception:
                    usage = None

        return ("".join(text_parts), tool_uses, usage)

    async def create(self, *, model: str, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]], max_tokens: int, temperature: float) -> Dict[str, Any]:
        def _do():
            kwargs: Dict[str, Any] = {
                "model": model,
                "system": system,
                "messages": messages,
                "max_tokens": int(max_tokens),
                "temperature": float(temperature),
            }
            if tools:
                kwargs["tools"] = tools
            return self._client.messages.create(**kwargs)

        msg = await asyncio.to_thread(_do)
        text, tool_uses, usage = self._extract_text_tool_uses_usage(msg)
        return {"text": text, "tool_uses": tool_uses, "usage": usage, "raw": msg}

    def stream(self, *, model: str, system: str, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]], max_tokens: int, temperature: float):
        loop = asyncio.get_running_loop()
        q: asyncio.Queue = asyncio.Queue()
        done = loop.create_future()

        def _run():
            text_parts: List[str] = []
            final_msg: Any = None
            err: Optional[BaseException] = None
            try:
                kwargs: Dict[str, Any] = {
                    "model": model,
                    "system": system,
                    "messages": messages,
                    "max_tokens": int(max_tokens),
                    "temperature": float(temperature),
                }
                if tools:
                    kwargs["tools"] = tools

                with self._client.messages.stream(**kwargs) as stream:
                    for event in stream:
                        try:
                            etype = getattr(event, "type", None)
                        except Exception:
                            etype = None

                        if etype == "text":
                            chunk = getattr(event, "text", None)
                            if isinstance(chunk, str) and chunk:
                                text_parts.append(chunk)
                                loop.call_soon_threadsafe(q.put_nowait, chunk)

                try:
                    if hasattr(stream, "get_final_message"):
                        final_msg = stream.get_final_message()
                    elif hasattr(stream, "final_message"):
                        final_msg = stream.final_message
                except Exception:
                    final_msg = None

            except BaseException as e:
                err = e

            if err is not None:
                loop.call_soon_threadsafe(done.set_exception, err)
            else:
                text, tool_uses, usage = self._extract_text_tool_uses_usage(final_msg) if final_msg is not None else ("".join(text_parts), [], None)
                loop.call_soon_threadsafe(done.set_result, {"text": text, "tool_uses": tool_uses, "usage": usage, "raw": final_msg})
            loop.call_soon_threadsafe(q.put_nowait, None)

        threading.Thread(target=_run, daemon=True).start()

        async def _gen():
            while True:
                item = await q.get()
                if item is None:
                    break
                yield item

        return _gen(), done


def build_tool_result_block(tool_use_id: str, content: Any) -> Dict[str, Any]:
    if isinstance(content, (dict, list)):
        payload = json.dumps(content, ensure_ascii=False)
    else:
        payload = str(content)
    return {"type": "tool_result", "tool_use_id": tool_use_id, "content": payload}
