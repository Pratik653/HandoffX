"""Run explicit assumed inputs; no real-agent calibration claim."""
import numpy as np
from handoffx import Action,ModelSet,Planner,State,TaskSpec
kernels=np.array([[[[.70,.01,.20,.09],[.75,.01,.15,.09],[.85,.01,.14,.00]]]])
models=ModelSet(kernels,np.array([[1.0]]),('elicited_example',),evidence_status='assumed')
controller=Planner(TaskSpec(action_cost=(.6,1.4,4.0)),models)
print(controller.recommend(State()).to_json())
print(controller.recommend(State().next(Action.CONTINUE,3)).to_json())
