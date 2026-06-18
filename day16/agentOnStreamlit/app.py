import streamlit as st

from planner import create_plan
from executor import execute_plan
from validator import validate
from llm_config import llm

st.set_page_config(
    page_title="Planner Executor Validator",
    layout="wide"
)

st.title("🤖 Planner → Executor → Validator Agent")

query = st.text_area(
    "Enter Task"
)

if st.button("Run Agent"):

    progress = st.progress(0)

    # Planner
    plan = create_plan(query, llm)
    progress.progress(30)

    # Executor
    execution_result = execute_plan(plan)
    progress.progress(70)

    # Validator
    validation = validate(
        query,
        execution_result,
        llm
    )

    progress.progress(100)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📋 Planner")
        st.write(plan)

    with col2:
        st.subheader("⚙️ Executor")

        for r in execution_result:
            st.success(r)

    with col3:
        st.subheader("✅ Validator")
        st.info(validation)