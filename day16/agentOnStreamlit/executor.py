def execute_plan(plan):

    steps = plan.split("\n")

    results = []

    for step in steps:

        if not step.strip():
            continue

        results.append(
            f"Executed: {step}"
        )

    return results