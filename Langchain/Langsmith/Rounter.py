from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnableLambda
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser

# Use Llama 3 local model via Ollama
llm = Ollama(model="llama3")

# 1) Router prompt: decide type of question
router_prompt = ChatPromptTemplate.from_template(
    "Classify the user query as 'math', 'code', or 'chat'.\n"
    "Query: {question}\n"
    "Answer with only one word."
)

router_chain = router_prompt | llm | StrOutputParser()

# 2) Define 3 separate chains (here kept simple)
math_prompt = ChatPromptTemplate.from_template(
    "You are a Python calculator. Solve: {question}"
)
math_chain = math_prompt | llm | StrOutputParser()

code_prompt = ChatPromptTemplate.from_template(
    "You are a coding tutor. Answer this coding question in detail: {question}"
)
code_chain = code_prompt | llm | StrOutputParser()

chat_prompt = ChatPromptTemplate.from_template(
    "You are a friendly assistant. Respond briefly to: {question}"
)
chat_chain = chat_prompt | llm | StrOutputParser()

# 3) Build the router using RunnableLambda + RunnableBranch
def route(info: dict) -> dict:
    """Call router_chain and attach the route label to the dict."""
    q = info["question"]
    label = router_chain.invoke({"question": q}).strip().lower()
    info["route"] = label
    return info

router = RunnableLambda(route)

app = (
    router
    | RunnableBranch(
        (lambda d: d["route"] == "math", math_chain),
        (lambda d: d["route"] == "code", code_chain),
        # default branch
        chat_chain,
    )
)

print(app.invoke({"question": "2 + 5 * 3"}))