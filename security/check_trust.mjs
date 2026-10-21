import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {X509Certificate} from 'node:crypto';
import tls from 'node:tls';

const blocked = new Set(JSON.parse(readFileSync(new URL('./blocked-roots.json', import.meta.url)))
  .map(root => root.sha256.toLowerCase()));
const version = process.versions.node.split('.').map(Number);
assert(version[0] === 24 && (version[1] > 22 || (version[1] === 22 && version[2] >= 1)),
  `Expected patched Node 24 >=24.22.1, got ${process.versions.node}`);
for (const type of ['default', 'bundled', 'system']) {
  const roots = tls.getCACertificates(type);
  assert(roots.length > 0, `${type}: empty trust store`);
  for (const pem of roots) {
    const fingerprint = new X509Certificate(pem).fingerprint256.replaceAll(':', '').toLowerCase();
    assert(!blocked.has(fingerprint), `${type}: compromised root remains trusted`);
  }
  console.log(`Node ${process.versions.node} ${type}: blocked roots absent (${roots.length} roots)`);
}
function handshake(host) {
  return new Promise((resolve, reject) => {
    const socket = tls.connect({host, port: 443, servername: host, rejectUnauthorized: true});
    socket.setTimeout(15000, () => socket.destroy(new Error(`TLS timeout: ${host}`)));
    socket.once('secureConnect', () => { socket.end(); resolve(); });
    socket.once('error', reject);
  });
}
if (process.argv.includes('--live')) {
  for (const host of ['www.google.com', 'slvshindex.ruwy.app']) {
    await handshake(host);
    console.log(`HTTPS accepted: ${host}`);
  }
  const hosts = ['dv', 'ov', 'ev'].flatMap(usage => ['g3b', 'g3c'].flatMap(generation =>
    ['', '-aaa'].map(cross => `${usage}-${generation}${cross}-emudhra.we-have-a-problem.com`)));
  const certificateErrors = new Set(['UNABLE_TO_GET_ISSUER_CERT', 'DEPTH_ZERO_SELF_SIGNED_CERT',
    'SELF_SIGNED_CERT_IN_CHAIN', 'UNABLE_TO_GET_ISSUER_CERT_LOCALLY',
    'UNABLE_TO_VERIFY_LEAF_SIGNATURE', 'CERT_REVOKED']);
  for (const host of hosts) {
    await assert.rejects(handshake(host), error => certificateErrors.has(error.code),
      `${host}: expected certificate rejection`);
  }
  console.log(`Compromised chains rejected: ${hosts.length}/${hosts.length}`);
}
