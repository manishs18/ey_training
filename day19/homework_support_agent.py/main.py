from agent import agent_application
from database import get_short_term_history
from langgraph.errors import GraphInterrupt

def run_simulation():
    # Thread identifier setup tracking session state across Redis
    thread_config = {"configurable": {"thread_id": "session_cus_1002"}}
    history = get_short_term_history("session_cus_1002")
    history.clear()

    # --- Scenario 1: Complex Multi-Tool Chaining Prompt ---
    user_input = "Hi! Please remember that I am an enterprise VIP tier client, check my order status, and kick off a full data system audit."
    print(f"\n[User Request]: {user_input}\n")
    history.add_user_message(user_input)

    for event in agent_application.stream({"messages": history.messages}, thread_config):
        for node, data in event.items():
            print(f"-> Node Processed: {node}")
            if "messages" in data:
                print(f"Log: {data['messages'][-1]}\n")

    # --- Scenario 2: Action Triggering Human In The Loop Interruption Gate ---
    critical_input = "I want a refund of $500 right now for this defective hardware profile."
    print(f"\n[User Request]: {critical_input}\n")
    
    # Sync current thread history
    updated_state = agent_application.get_state(thread_config)
    history.add_user_message(critical_input)

    try:
        # This execution thread should stop abruptly at the approval gate
        for event in agent_application.stream({"messages": history.messages}, thread_config):
            print(event)
    except GraphInterrupt:
        print("\n=== [GRAPH INTERRUPT] State Halted: Awaiting Executive Staff Validation ===")
        
        # Simulate supervisor console action override decision
        supervisor_override = "APPROVED"
        print(f"[Admin Panel Input Received]: {supervisor_override}")
        
        if supervisor_override == "APPROVED":
            # Apply approval flag updates directly onto the active transaction memory state
            agent_application.update_state(thread_config, {"action_approved": True}, as_node="human_approval_gate")
            print("=== [Graph Resuming] Authorization verified. Proceeding with execution pipeline. ===\n")
            
            for event in agent_application.stream(None, thread_config):
                for node, data in event.items():
                    print(f"-> Node Processed: {node}")
                    if "messages" in data:
                        print(f"Log: {data['messages'][-1]}\n")

if __name__ == "__main__":
    run_simulation()