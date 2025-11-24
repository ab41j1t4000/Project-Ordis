# from kernel.kernel import Kernel
# from kernel.tick import run_tick_loop
# from perception.text_ingest import ingest_chat
# from perception.file_ingest import scan_inbox
from kernel.kernel import main

if __name__ == "__main__":
    main()

    # k = Kernel()
    # try:
    #     # Week-2 perception smoke tests
    #     chat_evt = ingest_chat("Operator test message")
    #     k.ingest_event(chat_evt)

    #     for file_evt in scan_inbox():
    #         k.ingest_event(file_evt)

    #     # Week-4: consolidate episodic/world into semantic facts
    #     k.run_consolidation()

    #     # Week-5: run coherence evaluator
    #     k.run_eval()

    #     # then resume Week-1 heartbeat
    #     run_tick_loop(k.step, max_ticks=5)
    # finally:
    #     k.shutdown()
