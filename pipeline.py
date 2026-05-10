def extract_content(agent_result):
    try:
        messages = agent_result.get("messages", [])
        if messages:
            return getattr(messages[-1], "content", str(messages[-1]))
        return str(agent_result)
    except Exception:
        return str(agent_result)


def run_research_pipeline(topic: str) -> dict:
    # Lazy imports: fixes Render import error
    from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

    state = {
        "topic": topic,
        "search_result": "",
        "scraped_content": "",
        "report": "",
        "feedback": "",
    }

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            ("user", f"Find recent, reliable and detailed information about: {topic}")
        ]
    })

    state["search_result"] = extract_content(search_result)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"""
Based on these search results about "{topic}",
pick the most relevant URL and scrape it.

Search Results:
{state["search_result"][:1200]}
"""
            )
        ]
    })

    state["scraped_content"] = extract_content(reader_result)

    research_combined = f"""
TOPIC:
{topic}

SEARCH RESULTS:
{state["search_result"]}

SCRAPED CONTENT:
{state["scraped_content"]}
"""

    report = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    state["report"] = getattr(report, "content", str(report))

    feedback = critic_chain.invoke({
        "report": state["report"]
    })

    state["feedback"] = getattr(feedback, "content", str(feedback))

    return state


if __name__ == "__main__":
    topic = input("Enter research topic: ")
    result = run_research_pipeline(topic)
    print(result["report"])