"""Offline verification of the publisher's twelve PEM test chains."""
import base64
import io
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile


def verify(bundle):
    archive = zipfile.ZipFile(io.BytesIO(base64.b64decode(Path(__file__).with_name('chains.b64').read_text())))
    files = [name for name in archive.namelist() if name.endswith('.pem')]
    assert len(files) == 12
    with tempfile.TemporaryDirectory() as directory:
        for name in files:
            path = Path(directory) / Path(name).name
            path.write_bytes(archive.read(name))
            result = subprocess.run(['openssl', 'verify', '-CAfile', str(bundle), '-no-CApath', '-no-CAstore',
                                     '-untrusted', str(path), str(path)], capture_output=True, text=True)
            assert result.returncode != 0 and ('error 20 ' in result.stderr or 'error 2 ' in result.stderr), result.stdout + result.stderr
    print(f'Offline compromised chains rejected: 12/12 ({bundle})', flush=True)


if __name__ == '__main__':
    verify(sys.argv[1])
