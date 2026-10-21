"""Check runtime CA stores; --live also tests all 12 published compromised chains."""
import argparse
import concurrent.futures
import hashlib
import importlib.metadata
import json
from pathlib import Path
import socket
import ssl

ROOTS = json.loads(Path(__file__).with_name('blocked-roots.json').read_text())
BLOCKED = {r['sha256'].lower() for r in ROOTS}
HOSTS = [f'{usage}-{generation}{cross}-emudhra.we-have-a-problem.com'
         for usage in ('dv', 'ov', 'ev') for generation in ('g3b', 'g3c')
         for cross in ('', '-aaa')]


def check_store(label, cafile=None):
    context = ssl.create_default_context(cafile=cafile or "/etc/ssl/certs/ca-certificates.crt")
    present = {hashlib.sha256(c).hexdigest() for c in context.get_ca_certs(binary_form=True)}
    assert present, f'{label}: empty trust store'
    assert not present & BLOCKED, f'{label}: compromised roots remain trusted'
    print(f'{label}: blocked roots absent ({len(present)} trusted roots)', flush=True)
    return context


def handshake(host, context):
    with socket.create_connection((host, 443), timeout=15) as connection:
        with context.wrap_socket(connection, server_hostname=host):
            pass


def reject(host, context):
    try:
        handshake(host, context)
    except ssl.SSLCertVerificationError as error:
        assert error.verify_code in (2, 18, 19, 20, 21, 23), (host, error)
        return host
    raise AssertionError(f'{host}: compromised chain accepted')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--system-only', action='store_true')
    args = parser.parse_args()
    context = check_store('OS/Python')
    if not args.system_only:
        version = importlib.metadata.version('pip')
        assert tuple(map(int, version.split('.'))) >= (26, 2, 2), version
        from pip._vendor import certifi as pip_certifi
        check_store(f'pip {version}', pip_certifi.where())
        try:
            import certifi
        except ImportError:
            pass
        else:
            version = importlib.metadata.version('certifi')
            assert tuple(map(int, version.split('.'))) >= (2026, 10, 19), version
            check_store(f'certifi {version}', certifi.where())
    if args.live:
        for host in ('www.google.com', 'slvshindex.ruwy.app'):
            handshake(host, context)
            print(f'HTTPS accepted: {host}', flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            rejected = list(executor.map(lambda host: reject(host, context), HOSTS))
        print(f'Compromised chains rejected: {len(rejected)}/{len(HOSTS)}', flush=True)


if __name__ == '__main__':
    main()
