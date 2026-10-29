"""Attributed expected-loss algebra; no novel threshold theorem is claimed."""
from __future__ import annotations
from typing import Mapping
from math import isfinite

def expected_losses(probabilities:Mapping[str,float],costs:Mapping[str,float],
                    failure_loss:float,stop_loss:float|None=None)->dict[str,float]:
    if not isfinite(failure_loss) or failure_loss<0:raise ValueError('invalid failure loss')
    if set(probabilities)!=set(costs):raise ValueError('cost and probability keys differ')
    result={}
    for a,p in probabilities.items():
        c=costs[a]
        if not isfinite(p) or not 0<=p<=1 or not isfinite(c) or c<0:raise ValueError('invalid input')
        result[a]=c+(1-p)*failure_loss
    if stop_loss is not None:
        if not isfinite(stop_loss) or stop_loss<0:raise ValueError('invalid stop loss')
        result['stop']=stop_loss
    return result

def human_threshold(p_ai:float,c_ai:float,c_human:float,failure_loss:float)->float:
    if not isfinite(p_ai) or not 0<=p_ai<=1:raise ValueError('invalid AI probability')
    if any(not isfinite(v) or v<0 for v in (c_ai,c_human,failure_loss)) or failure_loss==0:
        raise ValueError('costs must be nonnegative and failure loss strictly positive')
    # Values outside [0,1] are deliberately retained: always/never feasible cases.
    return p_ai+(c_human-c_ai)/failure_loss
