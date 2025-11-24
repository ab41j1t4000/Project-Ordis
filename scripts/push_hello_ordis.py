from kernel.kernel import Kernel
from perception.events import Event


def main():
    k = Kernel()
    try:
        e = Event(
            event_type="chat",
            source="Abhijith",
            payload={"text": "Hello Ordis"},
        )
        k.ingest_event(e)  # logs + queues
        k.step()  # processes queue -> world -> semantic -> eval
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
