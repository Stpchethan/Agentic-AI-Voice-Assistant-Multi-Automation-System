from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain


def extract_content(agent_result):
    """
    Safely extracts final text from LangChain/LangGraph agent response.
    """
    try:
        messages = agent_result.get("messages", [])
        if messages:
            last_message = messages[-1]
            return getattr(last_message, "content", str(last_message))
        return str(agent_result)
    except Exception as e:
        return f"Error extracting agent output: {e}"


def run_research_pipeline(topic: str) -> dict:
    """
    Main research pipeline:
    1. Search Agent
    2. Reader Agent
    3. Writer Chain
    4. Critic Chain
    """

    state = {
        "topic": topic,
        "search_result": "",
        "scraped_content": "",
        "report": "",
        "feedback": "",
    }

    try:
        print("\n" + "=" * 50)
        print("STEP 1 - SEARCH AGENT WORKING")
        print("=" * 50)

        search_agent = build_search_agent()

        search_result = search_agent.invoke({
            "messages": [
                (
                    "user",
                    f"Find recent, reliable, and detailed information about: {topic}"
                )
            ]
        })

        state["search_result"] = extract_content(search_result)

        print("\nSEARCH RESULT:\n", state["search_result"])

    except Exception as e:
        state["search_result"] = f"Search agent failed: {e}"
        print(state["search_result"])

    try:
        print("\n" + "=" * 50)
        print("STEP 2 - READER AGENT WORKING")
        print("=" * 50)

        reader_agent = build_reader_agent()

        reader_result = reader_agent.invoke({
            "messages": [
                (
                    "user",
                    f"""
Based on the following search results about "{topic}",
pick the most relevant URL and scrape it for deeper content.

Search Results:
{state["search_result"][:1200]}
"""
                )
            ]
        })

        state["scraped_content"] = extract_content(reader_result)

        print("\nSCRAPED CONTENT:\n", state["scraped_content"])

    except Exception as e:
        state["scraped_content"] = f"Reader agent failed: {e}"
        print(state["scraped_content"])

    try:
        print("\n" + "=" * 50)
        print("STEP 3 - WRITER CHAIN WORKING")
        print("=" * 50)

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

        print("\nFINAL REPORT:\n", state["report"])

    except Exception as e:
        state["report"] = f"Writer chain failed: {e}"
        print(state["report"])

    try:
        print("\n" + "=" * 50)
        print("STEP 4 - CRITIC CHAIN WORKING")
        print("=" * 50)

        feedback = critic_chain.invoke({
            "report": state["report"]
        })

        state["feedback"] = getattr(feedback, "content", str(feedback))

        print("\nCRITIC FEEDBACK:\n", state["feedback"])

    except Exception as e:
        state["feedback"] = f"Critic chain failed: {e}"
        print(state["feedback"])

    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")

    result = run_research_pipeline(topic)

    print("\n" + "=" * 50)
    print("FINAL OUTPUT")
    print("=" * 50)

    print("\nREPORT:\n")
    print(result["report"])

    print("\nFEEDBACK:\n")
    print(result["feedback"])