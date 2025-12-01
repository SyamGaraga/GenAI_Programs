from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from langchain_core.output_parsers import StrOutputParser
from typing import Dict

# Use Llama 3 local model via Ollama
llm = Ollama(model="llama3")

answer_prompt = ChatPromptTemplate.from_template(
    "Use the documents below to answer the question.\n"
    "Question: {user_input}\n"
    "Documents: {documents}"
)

answer_chain = answer_prompt | llm | StrOutputParser()

def answer_node(state: Dict) -> Dict:
    answer = answer_chain.invoke(
        {"user_input": state["user_input"], "documents": state.get("documents", [])}
    )
    state["answer"] = answer
    return state

# Actually call the function to see output
test_state = {
    "user_input": "What is the capital of France?",
    "documents": ["Paris is the capital and largest city of France."]
}
result_state = answer_node(test_state)
print("Output:", result_state)