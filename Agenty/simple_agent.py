import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelRequest, ModelResponse, SystemPromptPart, UserPromptPart,
    TextPart, ToolCallPart, ToolReturnPart, RetryPromptPart,
)
from pydantic_ai.mcp import MCPServerStreamableHTTP, MCPToolset
from pydantic_ai.models.openai import OpenAIChatModel
from fastmcp import Client


load_dotenv()

MCP_URL = "http://localhost:8030/mcp"
mcp_server = MCPServerStreamableHTTP(url=MCP_URL)

agent = Agent(
    model=OpenAIChatModel("openai/gpt-4o"),
    mcp_servers=[mcp_server],
    system_prompt=(
        "You are a helpful assistant with access to math tools and data resources. "
        "Use the available tools and resources to answer questions accurately. For each "
        "operation you are about to perform, check first if there is a prompt instructing how to "
        "do it. \n Very important notoce: In your response put ONLY the result, without any text,"
        "explanation or any additional information. You are not allowed to type anything more "
        "than a single result value!"
    )
)


@agent.tool_plain
async def list_resources():
    async with Client(MCP_URL) as client:
        resources = await client.list_resources()
        return [{"uri": r.uri, "name": r.name, "description": r.description}
                for r in resources]


@agent.tool_plain
async def get_resource(uri: str):
    async with Client(MCP_URL) as client:
        result = await client.read_resource(uri)
        return result


@agent.tool_plain
async def list_prompts() -> list[dict]:
    async with Client(MCP_URL) as client:
        prompts = await client.list_prompts()
        return [
            {
                "name": p.name,
                "description": p.description,
                "arguments": [
                    {"name": a.name, "description": a.description, "required": a.required}
                    for a in (p.arguments or [])
                ],
            }
            for p in prompts
        ]


@agent.tool_plain
async def get_prompt(name: str, arguments: dict[str, int | str]) -> str:
    async with Client(MCP_URL) as client:
        result = await client.get_prompt(name, arguments)
        return str(result)


def print_agent_trace(result) -> None:
    print("=" * 60, "\nAGENT TRACE\n", "=" * 60)
    for i, message in enumerate(result.all_messages()):
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, SystemPromptPart):
                    print(f"\n[system prompt] {part.content[:80]}...")
                elif isinstance(part, UserPromptPart):
                    print(f"\n[user] {part.content}")
                elif isinstance(part, ToolReturnPart):
                    print(f"\n[tool return] {part.tool_name} → {str(part.content)[:200]}...")
                elif isinstance(part, RetryPromptPart):
                    print(f"\n[retry] {part.content}")
        elif isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, TextPart):
                    print(f"\n[model text] {part.content[:200]}...")
                elif isinstance(part, ToolCallPart):
                    print(f"\n[tool call] {part.tool_name}({part.args})")
    print("\n" + "=" * 60, f"\nUsage: {result.usage()}\n", "=" * 60 + "\n")


async def chat() -> None:
    history = []
    async with agent:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if user_input.lower() in ("exit", "quit", "q"):
                break
            if not user_input:
                continue
            result = await agent.run(user_input, message_history=history)
            history = result.all_messages()
            print_agent_trace(result)
            print(f"Agent: {result.output}\n")


if __name__ == "__main__":
    asyncio.run(chat())
