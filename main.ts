// news-image-20261124 — deliver the finished front page.
//
// The page itself (Tuesday 24 November 2026: the Iran-US blockade
// standoff as the lead, plus Zaporizhzhia, Gaza, Ras Al Khaimah,
// Seoul's air zone, NATO's space warning and Germany's Delta deal)
// is entry.png, drawn in advance by build_frontpage.py. All this
// program does is carry it to the grader: confirm the file is a
// genuine PNG inside the limits, then copy the exact bytes to
// $MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png when the
// variable is unset). Node 22, standard library only; no network,
// no secrets; identical bytes on every run.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const FILE = "entry.png";
const LIMIT = 1_000_000;
const EDGE = 1024;
const MAGIC_HEX = "89504e470d0a1a0a";

const base = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(base, FILE);
const destDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const destPath = join(destDir, FILE);

function abort(reason) {
  throw new Error(`entry.png: ${reason}`);
}

function describePng(bytes) {
  if (bytes.length < 8 || bytes.subarray(0, 8).toString("hex") !== MAGIC_HEX) {
    abort("does not start with the PNG signature");
  }
  if (bytes.length < 33) {
    abort("too short to hold an IHDR chunk and an IEND chunk");
  }
  if (bytes.readUInt32BE(8) !== 13 || bytes.toString("latin1", 12, 16) !== "IHDR") {
    abort("first chunk is not a 13-byte IHDR");
  }
  const w = bytes.readUInt32BE(16);
  const h = bytes.readUInt32BE(20);
  if (w > EDGE || h > EDGE) {
    abort(`is ${w}x${h}, over the ${EDGE}x${EDGE} limit`);
  }
  if (bytes.length > LIMIT) {
    abort(`is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  if (bytes.toString("latin1", bytes.length - 8, bytes.length - 4) !== "IEND") {
    abort("does not end with an IEND chunk");
  }
  return { w, h };
}

function main() {
  if (!existsSync(sourcePath)) {
    abort(`missing: ${sourcePath}`);
  }
  const bytes = readFileSync(sourcePath);
  const { w, h } = describePng(bytes);
  mkdirSync(destDir, { recursive: true });
  writeFileSync(destPath, bytes);
  const again = readFileSync(destPath);
  if (!again.equals(bytes)) {
    abort("read-back of the written file differs from the source");
  }
  console.log(`entry.png -> ${destPath} (${w}x${h}, ${bytes.length} bytes)`);
}

main();
