from typing import Callable, Optional

def run_tick_loop(step_fn: Callable[[], None], max_ticks: Optional[int] = None):
    """
    Deterministic heartbeat loop.
    - step_fn: called every tick
    - max_ticks: None => run forever, else stop after N ticks
    """
    tick_count = 0
    while True:
        step_fn()
        tick_count += 1

        if max_ticks is not None and tick_count >= max_ticks:
            break