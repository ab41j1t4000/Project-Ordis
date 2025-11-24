from kernel.kernel import Kernel


def main():
    k = Kernel()
    try:
        k.add_goal(
            goal_id="goal_1",
            description="Stabilize Ordis kernel + perception + memory pipeline",
            priority=10,
            meta={"owner": "Abhijith"},
        )
        print(k.list_goals())
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
