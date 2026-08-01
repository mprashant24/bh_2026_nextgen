import os
import warnings
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"  # Fix for OpenMP issue on macOS
warnings.filterwarnings("ignore", message=".*langchain-community.*")

from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.globals import set_debug

set_debug(False)

# Load Env Variables
from dotenv import load_dotenv

load_dotenv()

# For BedRock
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
faiss_db_path = os.path.join(SCRIPT_DIR, "..", "..", "vector_databases", "juice_shop.faiss")
db = FAISS.load_local(
    faiss_db_path,
    BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0"),
    allow_dangerous_deserialization=True,
)

retriever = db.as_retriever(
    search_type="mmr",  # Also test "similarity"
    search_kwargs={"k": 20},
)

system_prompt_template = """
You are a expert security code review analyst, with experience analyzing all types of source code for security vulnerabilities. You are meticulous about confirming technical details with code-backed justifications. Query the provided source code and provide detailed insights as requested.

Code for analysis:
{context}
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt_template),
        ("human", """<question>{question}</question>"""),
    ]
)

llm = ChatBedrock(
    model_id="qwen.qwen3-coder-30b-a3b-v1:0",
    model_kwargs={"temperature": 0.6},
)

chain = (
    {"context": retriever, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

user_question = """
Analyze the provided application and provide a detailed list of its purpose, functionality, and security impacting libraries and framworks. Identify possible potential security issues you can identify from the codebase provided in the context.
"""

# This is an optional addition to stream the output in chunks
# for a chat-like experience
for chunk in chain.stream(user_question):
    print(chunk, end="", flush=True)
