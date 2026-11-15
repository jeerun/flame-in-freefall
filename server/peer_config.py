"""Read a handheld's peer address as data and normalize dashboard origins."""
import ipaddress
import os
import re
import tempfile
from pathlib import Path


ORIGIN_FORMAT = "Use an HTTP(S) host and optional port, with no credentials, path, query or fragment."
DNS_LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", re.ASCII)


def normalize_origin(text, *, require_scheme=False):
    """Accept an origin, or a bare host[:port] for existing peer configurations."""
    if not text or len(text) > 512 or any(c.isspace() or not c.isprintable() for c in text):
        raise ValueError(ORIGIN_FORMAT)
    scheme, separator, authority = text.partition("://")
    if separator:
        scheme = scheme.lower()
        if scheme not in ("http", "https"):
            raise ValueError(ORIGIN_FORMAT)
    else:
        if require_scheme:
            raise ValueError(ORIGIN_FORMAT)
        scheme, authority = "http", text
    authority = authority.removesuffix("/")
    if not separator and not authority.startswith("[") and authority.count(":") > 1:
        authority = "[" + authority + "]"  # Bare IPv6 is an address; a port needs brackets.

    match = re.fullmatch(r"(\[[0-9A-Fa-f:.]+\]|[A-Za-z0-9.-]+)(?::([0-9]+))?", authority)
    if not match:
        raise ValueError(ORIGIN_FORMAT)
    host, port = match.groups()
    host = host.lower()
    if host.startswith("["):
        try:
            host = "[" + ipaddress.IPv6Address(host[1:-1]).compressed + "]"
        except ValueError:
            raise ValueError(ORIGIN_FORMAT) from None
    else:
        name = host.removesuffix(".")
        if len(name) > 253 or not all(DNS_LABEL.fullmatch(label) for label in name.split(".")):
            raise ValueError(ORIGIN_FORMAT)
        if re.fullmatch(r"[0-9.]+", name):
            try:
                ipaddress.IPv4Address(name)
            except ValueError:
                raise ValueError(ORIGIN_FORMAT) from None

    if port is not None:
        number = int(port)
        if not 1 <= number <= 65535:
            raise ValueError(ORIGIN_FORMAT)
        if number != (443 if scheme == "https" else 80):
            host += ":" + str(number)
    return scheme + "://" + host


def handheld_peer(path):
    """Use the saved origin or prompt once. A blank answer starts without a peer."""
    try:
        saved = path.read_text(encoding="utf-8-sig").removesuffix("\n")
    except FileNotFoundError:
        saved = ""
    if saved:
        try:
            return normalize_origin(saved)
        except ValueError:
            raise ValueError("Invalid address in pc-address.txt. Edit or remove the file. " + ORIGIN_FORMAT) from None

    value = input("PC dashboard address (for example http://192.168.1.23:8000), or Enter to run without the PC: ")
    if not value:
        return ""
    origin = normalize_origin(value)
    tmp = tempfile.NamedTemporaryFile(dir=path.parent, delete=False, mode="w", encoding="utf-8")
    temporary = Path(tmp.name)
    try:
        with tmp:
            tmp.write(origin + "\n")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)
    return origin
