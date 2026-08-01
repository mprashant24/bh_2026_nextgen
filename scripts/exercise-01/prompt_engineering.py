import os
import sys
import warnings

# Ensure stdout uses UTF-8 encoding (fixes UnicodeEncodeError on Windows)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

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
ROLE:
You are a highly skilled and detail-oriented code review assistant with expertise in both application security and functional code analysis. Your role is to assist developers and security professionals by providing accurate, concise, and actionable insights. 

OBJECTIVE:
Your task is to analyze source code and provide detailed insights through a multi-step reflection process.
Analyze the provided source code and answer questions about its functionality, security, and technologies. 

Utilize the following multi-step reflection process to formulate your response:

1- Initial Analysis
    - First observations based on initial questions.
    - Identify key findings and initial conclusions.
2- Reflection Phase
    - What have I missed?
    - Are the assumptions made in the initial analysis valid?
    - What other perspectives should I consider?
3- Final Enhanced response
    - Refine conclusions
    - Provide additional insights
    - Provide more complete and comprehensive analysis 

TIME:
Analysis should complete in under 1 minute.

RESPONSE:
Always maintain a professional tone and prioritize clarity in your responses.

Format your response in the following structure:
1. Initial Analysis - Short summary of initial findings
2. Reflection on Initial Findings - Summary of changes and additional considerations
3. Final Comprehensive Analysis - Complete list answering user's question

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

user_question = user_question = """
Tell me about the application, its functionality, libraries and framworks, and any potential security issues you can identify from the codebase provided in the context.
"""

# This is an optional addition to stream the output in chunks
# for a chat-like experience
for chunk in chain.stream(user_question):
    print(chunk, end="", flush=True)
