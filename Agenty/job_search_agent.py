import asyncio
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.messages import (
    ModelRequest, ModelResponse, SystemPromptPart, UserPromptPart,
    TextPart, ToolCallPart, ToolReturnPart, RetryPromptPart,
)
from pydantic_ai.mcp import MCPServerStreamableHTTP
from pydantic_ai.models.openai import OpenAIChatModel
from fastmcp import Client


load_dotenv()


MCP_URL = "http://localhost:8000/mcp"
mcp_server = MCPServerStreamableHTTP(url=MCP_URL)

agent = Agent(
    model=OpenAIChatModel("openai/gpt-4o"),
    mcp_servers=[mcp_server],
    system_prompt=(
        "You are a job search assistant specializing in finding job offers on nofluffjobs.com. "
        "You have access to tools for searching and scraping job listings. "
        "You have access to prompts which you can use to assess candidate's fit to a job offer "
        "and to create filters for the job search. "
        "You have also access to resources like the candidate resume and job expectations. "
        "When the user provides job search criteria, follow this workflow:\n"
        "1. Use `generate_search_url` to build a search URL from the given filters "
        "(work_model, technologies, salary_range, sort, etc.).\n"
        "2. Use `get_offers_from_search_url` to retrieve a list of job offer URLs from that search.\n"
        "3. Use `scrape_single_offer` to fetch details of individual offers when needed.\n"
        "If no offers are found, inform the user and suggest adjusting the filters."
    ),
)


@agent.tool_plain
async def list_resource() -> list[dict]:
    async with Client(MCP_URL) as client:
        resources = await client.list_resources()
        return [{"uri": str(r.uri), "name": r.name, "description": r.description} for r in resources]


@agent.tool_plain
async def get_resource(uri: str) -> str:
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
            print_agent_trace(result)
            print(f"Agent: {result.output}\n")

            history = result.all_messages()


if __name__ == "__main__":
    asyncio.run(chat())
