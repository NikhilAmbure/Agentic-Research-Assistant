import json

from django.http import JsonResponse, StreamingHttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agent import agent_graph



# Helpers
def extract_tools_used(messages: list) -> list[str]:
    """Return deduplicated list of tool names used in this invocation."""
    seen = []
    for msg in messages:
        if isinstance(msg, ToolMessage) and msg.name not in seen:
            seen.append(msg.name)
    return seen


def parse_body(request) -> dict:
    """Parse JSON request body safely."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}



# POST /api/chat/  — standard request / response
@method_decorator(csrf_exempt, name="dispatch")
class ChatView(View):

    def post(self, request):
        data = parse_body(request)
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default")

        if not message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        config = {"configurable": {"thread_id": session_id}}

        try:
            result = agent_graph.invoke(
                {"messages": [HumanMessage(content=message)]},
                config=config,
            )
        except Exception as e:
            return JsonResponse({"error": f"Agent error: {str(e)}"}, status=500)

        all_messages = result["messages"]
        response_text = all_messages[-1].content
        tools_used = extract_tools_used(all_messages)

        return JsonResponse({
            "response": response_text,
            "session_id": session_id,
            "tools_used": tools_used,
        })


# POST /api/chat/stream/  — Server-Sent Events
@method_decorator(csrf_exempt, name="dispatch")
class ChatStreamView(View):

    def post(self, request):
        data = parse_body(request)
        message = data.get("message", "").strip()
        session_id = data.get("session_id", "default")

        if not message:
            return JsonResponse({"error": "Message cannot be empty."}, status=400)

        config = {"configurable": {"thread_id": session_id}}

        def event_stream():
            try:
                for event in agent_graph.stream(
                    {"messages": [HumanMessage(content=message)]},
                    config=config,
                    stream_mode="updates",
                ):
                    for node_name, node_output in event.items():
                        msgs = node_output.get("messages", [])
                        for msg in msgs:

                            # Stream AI response tokens
                            if isinstance(msg, AIMessage) and msg.content:
                                payload = json.dumps({
                                    "type": "token",
                                    "node": node_name,
                                    "content": msg.content,
                                })
                                yield f"data: {payload}\n\n"

                            # Announce tool calls
                            if isinstance(msg, AIMessage) and getattr(msg, "tool_calls", []):
                                for tc in msg.tool_calls:
                                    payload = json.dumps({
                                        "type": "tool_start",
                                        "tool": tc["name"],
                                    })
                                    yield f"data: {payload}\n\n"

                            # Announce tool results
                            if isinstance(msg, ToolMessage):
                                payload = json.dumps({
                                    "type": "tool_end",
                                    "tool": msg.name,
                                })
                                yield f"data: {payload}\n\n"

            except Exception as e:
                payload = json.dumps({"type": "error", "content": str(e)})
                yield f"data: {payload}\n\n"
            finally:
                yield "data: [DONE]\n\n"

        response = StreamingHttpResponse(
            event_stream(),
            content_type="text/event-stream",
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        return response


# GET /api/history/<session_id>/
class HistoryView(View):

    def get(self, request, session_id: str):
        config = {"configurable": {"thread_id": session_id}}
        try:
            state = agent_graph.get_state(config)
            if not state or not state.values:
                return JsonResponse({"session_id": session_id, "messages": []})

            messages = []
            for msg in state.values.get("messages", []):
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage) and msg.content:
                    messages.append({"role": "assistant", "content": msg.content})

            return JsonResponse({"session_id": session_id, "messages": messages})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @method_decorator(csrf_exempt)
    def delete(self, request, session_id: str):
        # MemorySaver thread resets when no checkpoints remain
        return JsonResponse({
            "message": f"Session '{session_id}' cleared.",
            "session_id": session_id,
        })



# GET /api/health/

class HealthView(View):

    def get(self, request):
        return JsonResponse({
            "status": "running",
            "agent": "Multi-Tool AI Agent",
            "tools": ["web_search", "calculator", "python_executor", "file_reader"],
        })