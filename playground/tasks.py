from celery import shared_task
from time import sleep

@shared_task
def email_sender(message):
    """
    A simple example of a Celery task.
    

    :param message: Message to be processed
    :return: Processed message
    """

    print("Sending 10k emails...")
    result = f"Processed: {message}"
    print(result)
    sleep(3)
    print("Done. Sent 10k emails...")
