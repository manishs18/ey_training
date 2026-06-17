from azure.servicebus import ServiceBusClient

CONNECTION_STR = "SERVICE_BUS_CONNECTION"

QUEUE_NAME = "documents"

def process_message(message):

    print(message)

def start_worker():

    servicebus_client = ServiceBusClient.from_connection_string(
        CONNECTION_STR
    )

    receiver = servicebus_client.get_queue_receiver(
        queue_name=QUEUE_NAME
    )

    with receiver:

        for message in receiver:

            process_message(message)

            receiver.complete_message(
                message
            )

if __name__ == "__main__":
    start_worker()