from kernel import Kernel
from tick import run_tick_loop

if __name__ == "__main__":
    k = Kernel()
    try:
        run_tick_loop(k.step, max_ticks=5)  # run 5 ticks then stop
    finally:
        k.shutdown()