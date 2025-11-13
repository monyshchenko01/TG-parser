import asyncio
import csv
from telethon import TelegramClient, errors

api_id = XXX
api_hash = 'XXX'
phone = '+XXX'

channels = [
    "nexta_live",
    "nexta_ua",
    "truexanewsua",
    "ssternenko",
    "hromadske_ua",
    "stanislav_osman",

]

keywords_posts = ["корупція", "розкрадання", "взяточник", "зловживання", "коррупци"]
keywords_comments = ["донат", "donate", "збір", "monobank", "банка", "paypal"]

output_file = "telegram_comments_korupcia_donaty.csv"

client = TelegramClient('tg_session', api_id, api_hash)


async def main():
    await client.start(phone)
    print("✅ Telegram клієнт підключено")

    with open(output_file, mode="w", newline='', encoding="utf-8") as csv_file:
        fieldnames = ["channel", "post_id", "post_text", "comment_text"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for channel_username in channels:
            try:
                print(f"\n📡 Перевіряю канал: {channel_username}")
                entity = await client.get_entity(channel_username)
                print(f"✅ Канал {channel_username} існує")

                async for message in client.iter_messages(entity, limit=100000):
                    if not message.message:
                        continue

                    text_lower = message.message.lower()
                    if any(keyword in text_lower for keyword in keywords_posts):
                        try:
                            replies = await client.get_messages(entity, reply_to=message.id, limit=50000)
                            for r in replies:
                                if r and r.message:
                                    comment_text = r.message.lower()
                                    if any(k in comment_text for k in keywords_comments):

                                        writer.writerow({
                                            "channel": channel_username,
                                            "post_id": message.id,
                                            "post_text": message.message.replace("\n", " "),
                                            "comment_text": r.message.replace("\n", " ")
                                        })
                        except errors.rpcerrorlist.MsgIdInvalidError:
                            continue
                        except Exception as e:
                            print(f"⚠️ Помилка при отриманні коментарів для {channel_username}: {e}")

            except ValueError:
                print(f"❌ Канал {channel_username} не знайдено або приватний")
            except Exception as e:
                print(f"⚠️ Помилка з каналом {channel_username}: {e}")

    print(f"\n✅ Дані збережено у {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
