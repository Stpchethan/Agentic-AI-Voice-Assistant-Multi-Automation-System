from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage

from tools import web_search, scrape_url


fast_llm = ChatOllama(
    model="llama3.2:1b",
    temperature=0
)

smart_llm = ChatOllama(
    model="llama3.2:latest",
    temperature=0
)


class SimpleToolAgent:
    def __init__(self, tool, system_prompt):
        self.tool = tool
        self.system_prompt = system_prompt

    def invoke(self, inputs):
        user_message = inputs["messages"][-1][1]

        tool_result = self.tool.invoke(user_message)

        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """
User request:
{user_message}

Tool result:
{tool_result}

Now give a clean, useful response.
""")
        ])

        chain = prompt | fast_llm | StrOutputParser()

        final_response = chain.invoke({
            "user_message": user_message,
            "tool_result": tool_result
        })

        return {
            "messages": [
                AIMessage(content=final_response)
            ]
        }


def build_search_agent():
    return SimpleToolAgent(
        tool=web_search,
        system_prompt=(
            "You are a search agent. Summarize reliable search results clearly. "
            "Include useful URLs if available."
        )
    )


def build_reader_agent():
    return SimpleToolAgent(
        tool=scrape_url,
        system_prompt=(
            "You are a reader agent. Extract the most important information "
            "from scraped webpage content."
        )
    )


writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, factual reports."),
    ("human", """
Write a detailed research report.

Topic: {topic}

Research:
{research}

Structure:
- Introduction
- Key Findings
- Conclusion
- Sources

Be detailed, factual, and professional.
""")
])

writer_chain = writer_prompt | smart_llm | StrOutputParser()


critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict research critic. Be honest, specific, and constructive."),
    ("human", """
Review this report:

{report}

Format:

Score: X/10

Strengths:
- ...

Areas to Improve:
- ...
""")
])

critic_chain = critic_prompt | smart_llm | StrOutputParser()