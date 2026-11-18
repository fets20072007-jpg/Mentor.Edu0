from pathlib import Path
import base64
import secrets
from cryptography.hazmat.primitives.asymmetric import ec

ROOT = Path.cwd()
ENV = ROOT / ".env"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def generate_vapid():
    key = ec.generate_private_key(ec.SECP256R1())
    numbers = key.private_numbers()
    private_raw = numbers.private_value.to_bytes(32, "big")
    public = numbers.public_numbers
    public_raw = b"\\x04" + public.x.to_bytes(32, "big") + public.y.to_bytes(32, "big")
    return b64url(private_raw), b64url(public_raw)


def upsert_env(text: str, key: str, value: str) -> str:
    lines = text.splitlines()
    output = []
    replaced = False
    for line in lines:
        if line.startswith(key + "="):
            output.append(f"{key}={value}")
            replaced = True
        else:
            output.append(line)
    if not replaced:
        if output and output[-1].strip():
            output.append("")
        output.append(f"{key}={value}")
    return "\n".join(output) + "\n"

existing = ENV.read_text(encoding="utf-8") if ENV.exists() else ""
private_key, public_key = generate_vapid()
cron_token = secrets.token_urlsafe(32)

values = {
    "VAPID_PRIVATE_KEY": private_key,
    "VAPID_PUBLIC_KEY": public_key,
    "VAPID_SUBJECT": "mailto:contato@mentor.edu",
    "FOCUS_PUSH_CRON_TOKEN": cron_token,
    "FOCUS_PUSH_INTERVAL_SECONDS": "60",
}

for key, value in values.items():
    existing = upsert_env(existing, key, value)

ENV.write_text(existing, encoding="utf-8")

print("\n===============================================")
print(" MENTOR.EDU - WEB PUSH CONFIGURADO")
print("===============================================\n")
print("As chaves foram gravadas em .env.")
print("NÃO envie VAPID_PRIVATE_KEY ao GitHub.\n")
print("VAPID_PUBLIC_KEY:")
print(public_key)
print("\nFOCUS_PUSH_CRON_TOKEN:")
print(cron_token)
print("\nGuarde esses dois valores para o deploy depois.")
