import asyncio
import sys

try:
    from telethon import TelegramClient, errors
    from telethon.tl.functions.auth import SendCodeRequest, SignInRequest, CheckPasswordRequest
    from telethon.tl.functions.account import GetPasswordRequest
    from telethon.tl.functions.payments import GetPaymentFormRequest, SendStarsFormRequest
    from telethon.tl.types import InputInvoiceStarGift, TextWithEntities, CodeSettings
    from telethon.password import compute_check
except ImportError:
    sys.exit(1)

API_ID = 0
API_HASH = ""


async def send_gift():
    client = TelegramClient(
        "gift_session", API_ID, API_HASH,
        device_model="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        system_version="Win32",
        app_version="5.9.0 K",
        lang_code="en",
        system_lang_code="en-US",
    )

    await client.connect()

    if not await client.is_user_authorized():
        phone = input().strip()
        try:
            result = await client(SendCodeRequest(
                phone_number=phone,
                api_id=API_ID,
                api_hash=API_HASH,
                settings=CodeSettings(
                    allow_flashcall=False,
                    current_number=False,
                    allow_app_hash=False,
                )
            ))
        except Exception:
            await client.disconnect()
            return

        phone_code_hash = result.phone_code_hash

        code = input().strip()
        try:
            await client(SignInRequest(
                phone_number=phone,
                phone_code_hash=phone_code_hash,
                phone_code=code,
            ))
        except errors.SessionPasswordNeededError:
            password = input().strip()
            pwd = await client(GetPasswordRequest())
            await client(CheckPasswordRequest(password=compute_check(pwd, password)))

    await client.get_me()

    gift_id_str = input().strip()
    if not gift_id_str.isdigit():
        await client.disconnect()
        return
    gift_id = int(gift_id_str)

    message_text = input().strip()

    recipient = input().strip()
    if not recipient:
        await client.disconnect()
        return

    try:
        if recipient.lstrip("@").isdigit():
            user = await client.get_entity(int(recipient.lstrip("@")))
        else:
            user = await client.get_entity(recipient)
    except Exception:
        await client.disconnect()
        return

    msg = None
    if message_text:
        msg = TextWithEntities(text=message_text, entities=[])

    input_peer = await client.get_input_entity(user)
    invoice = InputInvoiceStarGift(
        peer=input_peer,
        gift_id=gift_id,
        message=msg,
    )

    try:
        form = await client(GetPaymentFormRequest(invoice=invoice))
        await client(SendStarsFormRequest(
            form_id=form.form_id,
            invoice=invoice,
        ))
    except Exception:
        pass

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(send_gift())
