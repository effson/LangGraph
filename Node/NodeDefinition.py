from functools import partial
from typing import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.types import RetryPolicy
from requests import RequestException, Timeout


# 定义state
class GraphState(TypedDict):
    process_data: dict


# 定义节点，入参:state
def input_node(state: GraphState) -> GraphState:
    print(f'input_node收到的初始值:{state}')
    return {"process_data": {"input": "input_value"}}

# 定义带参数node节点
def process_node(state: dict, param1: int, param2: str) -> dict:
    print(state, param1, param2)
    return {"process_data": {"process": "process_value"}}


# 重试策略,add_node方法时可选
retry_policy = RetryPolicy(
    max_attempts=3,                       # 最大重试次数
    initial_interval=1,                   # 初始间隔
    jitter=True,                          # 抖动（添加随机性避免重试风暴）
    backoff_factor=2,                     # 退避乘数（每次重试间隔时间的增长倍数）
    retry_on=[RequestException, Timeout]  # 只重试这些异常
)


stateGraph = StateGraph(GraphState)
# 添加inpu节点
stateGraph.add_node("input", input_node)
# 给process_node节点绑定参数
process_with_params = partial(process_node, param1=100, param2="test")
# 添加带参数的node节点
stateGraph.add_node("process", process_with_params,retry=retry_policy)

stateGraph.add_edge(START, "input")
stateGraph.add_edge("input", "process")
stateGraph.add_edge("process", END)

graph = stateGraph.compile()


print(stateGraph.edges)
print(stateGraph.nodes)
print(graph.get_graph().print_ascii())

print()

initial_state={"process_data": 5}
result= graph.invoke(initial_state)
print(f"最后的结果是:{result}")

"""
{('input', 'process'), ('__start__', 'input'), ('process', '__end__')}
{
'input': 
    StateNodeSpec(runnable=input(tags=None, recurse=True, explode_args=False, func_accepts={}), metadata=None, input_schema=<class '__main__.GraphState'>, 
                retry_policy=None, cache_policy=None, ends=(), defer=False), 
'process': 
    StateNodeSpec(runnable=process(tags=None, recurse=True, explode_args=False, func_accepts={}), metadata=None, input_schema=<class '__main__.GraphState'>, 
                retry_policy=RetryPolicy(initial_interval=1, backoff_factor=2, max_interval=128.0, max_attempts=3, jitter=True, retry_on=[<class 'requests.exceptions.RequestException'>, <class 'requests.exceptions.Timeout'>]), 
                cache_policy=None, ends=(), defer=False)
}
+-----------+  
| __start__ |  
+-----------+  
      *        
      *        
      *        
  +-------+    
  | input |    
  +-------+    
      *        
      *        
      *        
 +---------+   
 | process |   
 +---------+   
      *        
      *        
      *        
 +---------+   
 | __end__ |   
 +---------+   
None

input_node收到的初始值:{'process_data': 5}
{'process_data': {'input': 'input_value'}} 100 test
最后的结果是:{'process_data': {'process': 'process_value'}}
"""
