import numpy as np

def hallucination_risk(fact, hhem, bert, selfcheck):
    return (
        (1 - fact) * 0.3 +
        hhem * 0.3 +
        (1 - bert) * 0.2 +
        (1 - selfcheck) * 0.2
    )