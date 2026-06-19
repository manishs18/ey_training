
import os
import tempfile
import operator

import streamlit as st

from dotenv import load_dotenv
from typing import TypedDict, Annotated, List, Literal
from pydantic import BaseModel, Field

from transformers import pipeline

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

from langgraph.graph import StateGraph, END

load_dotenv()

# -----------------------------
# LLM + SEARCH
# -----------------------------

llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0
)

search_tool = TavilySearchResults(k=2)

emotion_model = pipeline(
    "audio-classification",
    model="superb/wav2vec2-base-superb-er"
)

# -----------------------------
# STATE
# -----------------------------

class AgentState(TypedDict):
    task: str
    audio_path: str
    emotion: str
    research_notes: Annotated[List[str], operator.add]
    draft: str
    next_node: str

# -----------------------------
# ROUTER
# -----------------------------

class Router(BaseModel):

    next_worker: Literal[
        "emotion_detector",
        "researcher",
        "writer",
        "FINISH"
    ]

    instructions: str

# -----------------------------
# EMOTION DETECTOR
# -----------------------------

def emotion_detector(state):

    result = emotion_model(
        state["audio_path"]
    )

    return {
        "emotion": result[0]["label"]
    }

# -----------------------------
# RESEARCHER
# -----------------------------

def researcher(state):

    query = f"""
    Explain emotion:
    {state['emotion']}
    """

    results = search_tool.invoke(query)

    return {
        "research_notes": [str(results)]
    }

# -----------------------------
# WRITER
# -----------------------------

def writer(state):

    notes = "\n".join(
        state["research_notes"]
    )

    prompt = f"""
    Generate a report.

    Emotion:
    {state['emotion']}

    Research:
    {notes}
    """

    report = llm.invoke(prompt)

    return {
        "draft": report.content
    }

# -----------------------------
# SUPERVISOR
# -----------------------------

def supervisor(state):

    structured_llm = llm.with_structured_output(
        Router
    )

    prompt = f"""
    Emotion:
    {state.get('emotion','')}

    Notes:
    {len(state['research_notes'])}

    Draft:
    {state['draft']}

    Routing Rules:

    No emotion ->
    emotion_detector

    Emotion but no notes ->
    researcher

    Notes but no draft ->
    writer

    Draft exists ->
    FINISH
    """

    decision = structured_llm.invoke(
        prompt
    )

    return {
        "next_node": decision.next_worker
    }

# -----------------------------
# GRAPH
# -----------------------------

builder = StateGraph(
    AgentState
)

builder.add_node(
    "supervisor",
    supervisor
)

builder.add_node(
    "emotion_detector",
    emotion_detector
)

builder.add_node(
    "researcher",
    researcher
)

builder.add_node(
    "writer",
    writer
)

builder.set_entry_point(
    "supervisor"
)

builder.add_conditional_edges(
    "supervisor",
    lambda x: x["next_node"],
    {
        "emotion_detector":
        "emotion_detector",

        "researcher":
        "researcher",

        "writer":
        "writer",

        "FINISH":
        END
    }
)

builder.add_edge(
    "emotion_detector",
    "supervisor"
)

builder.add_edge(
    "researcher",
    "supervisor"
)

builder.add_edge(
    "writer",
    "supervisor"
)

graph = builder.compile()

# -----------------------------
# STREAMLIT UI
# -----------------------------

st.title(
    "Voice Emotion Detection using LangGraph"
)

audio_file = st.file_uploader(
    "Upload WAV File",
    type=["wav"]
)

if audio_file:

    st.audio(audio_file)

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    ) as temp_file:

        temp_file.write(
            audio_file.read()
        )

        path = temp_file.name

    if st.button(
        "Analyze Emotion"
    ):

        result = graph.invoke(
            {
                "task":
                "Voice Emotion Detection",

                "audio_path":
                path,

                "emotion":
                "",

                "research_notes":
                [],

                "draft":
                "",

                "next_node":
                ""
            }
        )

        st.success(
            "Analysis Complete"
        )

        st.subheader(
            "Detected Emotion"
        )

        st.write(
            result["emotion"]
        )

        st.subheader(
            "Generated Report"
        )

        st.write(
            result["draft"]
        )
