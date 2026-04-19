"""
LangGraph中一个Graph可以单独使用，还可以作为一个Node嵌入到一个Graph中,称为子图。子图和Node没有太多的区别。

!!!唯一需要注意的是，触发SubGraph代表的Node后，重新调用了一次subgraph.invoke(state)方法

案例说明：
    定义一个子图节点处理函数 sub_node，它接收一个状态对象并返回包含子图响应消息的新状态。
    该函数被集成到一个使用 langgraph 构建的图结构中，最终执行图并输出结果。
"""

from operator import add
from typing import TypedDict, Annotated
from langgraph.constants import END
from langgraph.graph import StateGraph, MessagesState, START
import operator

class State(TypedDict):
    """
    messages: 使用add函数合并的字符串列表消息
    add 是 LangGraph 内置的状态合并策略，它的行为是：将新返回的列表与原状态中的列表进行拼接（而非覆盖）
    """
    messages: Annotated[list[str], add]

def sub_node(state:State) -> State:
    # @param state 当前状态对象，包含消息列表
    # @return 包含子图响应消息的新状态
    return {"messages": ["response from subgraph"]}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node("sub_node", sub_node)

subgraph_builder.add_edge(START, "sub_node")
subgraph_builder.add_edge("sub_node", END)
subgraph = subgraph_builder.compile()

# 创建主图构建器并添加子图节点
builder = StateGraph(State)
builder.add_node("subgraph_node", subgraph)
builder.add_edge(START, "subgraph_node")
builder.add_edge("subgraph_node", END)

# 编译主图并绘制结构图
graph = builder.compile()

# 执行图并打印结果

print(graph.invoke({"messages": ["main-graph"]}))
'''
子图调用的状态传递逻辑当主图调用子图节点时，整个过程会触发两次状态合并：
1：主图state: {"messages": ["main-graph"]} ------> 子图
2：子图: 执行 sub_node，add ------> ["main-graph", "response from subgraph"]
3：主图 :add，主图原有的 ["main-graph"] + 子图返回["main-graph", "response from subgraph"]
     ------> ["main-graph", "main-graph", "response from subgraph"]
'''
print()# {'messages': ['main-graph', 'main-graph', 'response from subgraph']}

#绘制子图结构图
print(subgraph.get_graph().draw_mermaid())

"""
{'messages': ['main-graph', 'main-graph', 'response from subgraph']}
"""
