from kernel.kernel import GoalEvent


def g_high_handler(k):
    return GoalEvent(payload={"msg": "g_high tick", "goal_id": "g_high"})
