import sys
import os
import json
import logging
import sqlite3

import pika

from settings import Settings


settings: Settings = Settings()
logging.basicConfig(level=logging.INFO)


def main() -> None:
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=str(settings.Rabbit_host))
    )
    channel = connection.channel()

    channel.queue_declare(queue=str(settings.Rabbit_chanel))

    def delete_user(user_id: int):
        con = sqlite3.connect("habits.db")
        cur = con.cursor()
        habits_db = cur.execute(
            "SELECT id FROM habits WHERE user_id = ?", (user_id,)
        ).fetchall()
        habits_list = [i[0] for i in habits_db]
        for i in habits_list:
            cur.execute("DELETE FROM trackers WHERE habit_id = ?", (i,))
        cur.execute("DELETE FROM habits WHERE user_id = ?", (user_id,))
        con.commit()
        logging.info("Habits | user_id: %s, status: deleted", user_id)

    def callback(ch, method, properties, body):
        logging.info("Received message: %s", body)
        data = json.loads(body)
        delete_user(int(data["deleted"]))

    channel.basic_consume(
        queue=str(settings.Rabbit_chanel), on_message_callback=callback, auto_ack=True
    )

    logging.info("Waiting for messages.")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
