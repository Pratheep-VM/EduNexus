import asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

# Import the bridge you just built
from mcp_bridge import MCPBridge 

async def run_agent(query: str) -> str:
    bridge = MCPBridge("mcp_server/server.py")
    await bridge.connect()
    
    try:
        tools = await bridge.get_langchain_tools()
        print(f"Loaded {len(tools)} tools from MCP.")

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        agent_executor = create_react_agent(llm, tools)

        inputs = {"messages": [HumanMessage(content=query)]}
        response = await agent_executor.ainvoke(inputs)
        
        final_message = response["messages"][-1]
        return final_message.content

    finally:
        await bridge.disconnect()

# If running directly from the terminal (for testing)
if __name__ == "__main__":
    async def test():
        ans = await run_agent("Use your tool to tell me the weather in Tokyo!")
        print("\nFinal Answer:", ans)
    asyncio.run(test())