from hashlib import sha1


def create_client_fingerprint(
        ip: str,
        user_agent: str,
        languages: str,
        encodings: str,
) -> str:
    return sha1(f"{ip}{user_agent}{languages}{encodings}".encode()).hexdigest()
