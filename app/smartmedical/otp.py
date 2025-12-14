import base64
import hmac
import hashlib
import struct
import time

def generate_otp(secret_base32: str, timestamp: int | None = None, step: int = 30, digits: int = 6) -> str:
    # Google Authenticator secrets are typically Base32 (case-insensitive, may have spaces)
    s = secret_base32.replace(" ", "").upper()
    key = base64.b32decode(s + "=" * ((8 - len(s) % 8) % 8))  # pad to multiple of 8

    if timestamp is None:
        timestamp = int(time.time())

    counter = timestamp // step
    msg = struct.pack(">Q", counter)

    h = hmac.new(key, msg, hashlib.sha1).digest()  # SHA1 is the common default for GA
    offset = h[-1] & 0x0F
    code_int = (struct.unpack(">I", h[offset:offset+4])[0] & 0x7FFFFFFF) % (10 ** digits)

    return str(code_int).zfill(digits)