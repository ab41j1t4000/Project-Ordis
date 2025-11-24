from kernel.kernel import Kernel


def main():
    k = Kernel()
    try:
        k.reset_safe_mode()
        print("SAFE_MODE reset.")
    finally:
        k.shutdown()


if __name__ == "__main__":
    main()
