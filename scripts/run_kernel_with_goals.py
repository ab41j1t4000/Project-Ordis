from kernel.kernel import Kernel
from goals.handlers import g_high_handler


def main():
    k = Kernel()
    try:
        k.register_goal_handler("g_high", g_high_handler)
        print("REGISTERED:", k.goal_handlers.keys())  # <-- ADD THIS LINE

        for _ in range(5):
            k.step()
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
