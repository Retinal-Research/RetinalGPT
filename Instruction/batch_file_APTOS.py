from batch_runner import run_named_batch_job


def create_batch_file():
    run_named_batch_job("APTOS")


def unpakced_output():
    run_named_batch_job("APTOS_unpack")


if __name__ == "__main__":
    create_batch_file()
