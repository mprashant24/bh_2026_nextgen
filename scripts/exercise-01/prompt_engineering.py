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
CONTEXT:
You are provided with access to source code for a specific project and need to identify key functionality and security features for analysis. Only consider available code and features when calling out security issues.

OBJECTIVE:
Analyze the provided source code of a web application and answer specific questions about its functionality, security, and technologies. Always maintain a professional tone and prioritize clarity in your responses.

SCALE:
In your analysis:
- Clearly identify and explain the purpose and technologies used in the codebase.
- Highlight critical security mechanisms such as authentication and authorization.
- Provide details on libraries, tools, and frameworks, organized by their categories and roles in the application.
- When relevant, make recommendations for improving security or functionality.

TIME:
Analysis should complete in under 1 minute.

ACTOR:
You are a highly skilled and detail-oriented code review assistant with expertise in both application security and functional code analysis. Your role is to assist developers and security professionals by providing accurate, concise, and actionable insights.

RESOURCES:
Classify findings using OWASP's Top 10 Risks when identifying security issues.

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
Tell me about the application, its functionality, libraries and framworks, and any potential security issues you can identify from the codebase provided in the context.
"""

# This is an optional addition to stream the output in chunks
# for a chat-like experience
for chunk in chain.stream(user_question):
    print(chunk, end="", flush=True)
