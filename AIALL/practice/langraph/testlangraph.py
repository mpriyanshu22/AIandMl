from langgraph.graph import StateGraph, MessagesState, START, END
from langsmith import wrappers
def mock_llm(state: MessagesState):
    return {"messages":[{"role":"ai","content":"hello every one !"}]}

graph= StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START,"mock_llm")
graph.add_edge("mock_llm",END)
graph=graph.compile() 
result = graph.invoke({"messages": [{"role": "user", "content": "hi!"}]})
print(result)
# print(graph.get_state("mock_llm"))  