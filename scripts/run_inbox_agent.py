import time
from kernel.kernel import Kernel
from perception.file_ingest import scan_inbox


def main(poll_seconds: int = 5, max_ticks: int | None = None):
    k = Kernel()
    ticks = 0
    try:
        while True:
            # 1) perceive
            events = scan_inbox()

            # 2) enqueue into kernel
            for e in events:
                k.ingest_event(e)

            # 3) run one deterministic tick
            k.step()
            ticks += 1

            if max_ticks is not None and ticks >= max_ticks:
                break

            time.sleep(poll_seconds)
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
