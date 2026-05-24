from agents import (
    build_reader_agent,
    build_search_agent,
    writer_chain,
    critic_chain
)


def extract_clean_text(content):

    """
    Convert structured LangChain response
    into clean readable text.
    """

    # if already string
    if isinstance(content, str):
        return content

    clean_text = ""

    # if structured list response
    if isinstance(content, list):

        for item in content:

            if isinstance(item, dict):

                # extract text blocks
                if item.get("type") == "text":

                    clean_text += item.get("text", "") + "\n"

    return clean_text.strip()


def run_research_pipeline(topic: str) -> dict:

    state = {}

    # ==================================================
    # STEP 1 - SEARCH AGENT
    # ==================================================

    print("\n" + "=" * 50)
    print("STEP 1 - SEARCH AGENT IS WORKING ...")
    print("=" * 50)

    search_agent = build_search_agent()

    search_result = search_agent.invoke({
        "messages": [
            (
                "user",
                f"Find recent, reliable and detailed information about: {topic}"
            )
        ]
    })

    # extract raw response
    raw_search_content = search_result["messages"][-1].content

    # clean response
    state["search_results"] = extract_clean_text(
        raw_search_content
    )

    print("\nSEARCH RESULT:\n")
    print(state["search_results"])

    # ==================================================
    # STEP 2 - READER AGENT
    # ==================================================

    print("\n" + "=" * 50)
    print("STEP 2 - READER AGENT IS SCRAPING TOP RESOURCES ...")
    print("=" * 50)

    reader_agent = build_reader_agent()

    reader_result = reader_agent.invoke({
        "messages": [
            (
                "user",
                f"""
Based on the following search results about '{topic}':

1. Pick the MOST relevant URL
2. Scrape the webpage
3. Extract detailed useful information
4. Return only clean readable content

Search Results:
{state['search_results'][:1500]}
"""
            )
        ]
    })

    # extract raw scraped response
    raw_reader_content = reader_result["messages"][-1].content

    # clean scraped content
    state["scraped_content"] = extract_clean_text(
        raw_reader_content
    )

    print("\nSCRAPED CONTENT:\n")
    print(state["scraped_content"])

    # ==================================================
    # STEP 3 - WRITER CHAIN
    # ==================================================

    print("\n" + "=" * 50)
    print("STEP 3 - WRITER IS DRAFTING THE REPORT ...")
    print("=" * 50)

    research_combined = f"""
SEARCH RESULTS:
{state['search_results']}

DETAILED SCRAPED CONTENT:
{state['scraped_content']}
"""

    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })

    print("\nFINAL REPORT:\n")
    print(state["report"])

    # ==================================================
    # STEP 4 - CRITIC AGENT
    # ==================================================

    print("\n" + "=" * 50)
    print("STEP 4 - CRITIC IS REVIEWING THE REPORT ...")
    print("=" * 50)

    state["feedback"] = critic_chain.invoke({
        "report": state["report"]
    })

    print("\nCRITIC FEEDBACK:\n")
    print(state["feedback"])

    return state


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    topic = input("\nEnter a research topic: ")

    run_research_pipeline(topic)