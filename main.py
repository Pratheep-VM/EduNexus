import asyncio
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

# Import the bridge you just built
from mcp_bridge import MCPBridge 

async def main():
    # 1. Start the Bridge
    bridge = MCPBridge("mcp_server/server.py")
    await bridge.connect()
    
    try:
        # 2. Get the tools
        tools = await bridge.get_langchain_tools()
        print(f"Loaded {len(tools)} tools from MCP.")

        # 3. Setup the LLM
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

        # 4. Build the LangGraph Agent
        # create_react_agent replaces AgentExecutor and create_tool_calling_agent
        agent_executor = create_react_agent(llm, tools)

        # 5. Test it!
        # LangGraph expects structured messages
        inputs = {"messages": [HumanMessage(content="Use your tool to tell me the weather in Tokyo!")]}
        
        # We async stream or invoke the graph
        response = await agent_executor.ainvoke(inputs)
        
        # LangGraph returns a state dictionary containing all the messages. 
        # The final answer is the content of the last message in the sequence.
        final_message = response["messages"][-1]
        print("\nFinal Answer:", final_message.content)

    finally:
        # Always disconnect to prevent zombie processes!
        await bridge.disconnect()

if __name__ == "__main__":
    asyncio.run(main())