// news-image-20261124: entry point.
//
// The front page itself is entry.png, rendered in advance by
// build_frontpage.py (a 1024x1024 page of THE WORLD for Tuesday
// 24 November 2026: the Iran-US naval blockade standoff, the Russian
// strike on Zaporizhzhia, the Gaza strikes, the Ras Al Khaimah bus
// crash, Russian jets in South Korea's air zone, NATO's space warning
// and Germany's Delta deal). This program's only job is to hand that
// finished page to the grader: read the PNG, check it is a genuine
// PNG inside the gate limits, and write the exact same bytes to
// $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
//
// Node 22, standard library only. No network access, no secrets.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// The finished page, rendered in advance by build_frontpage.py.
const FILE_NAME = "entry.png";
const MAX_BYTES = 1_000_000;
const MAX_EDGE = 1024;
const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, FILE_NAME);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outDir, FILE_NAME);

function fail(message) {
  throw new Error(`entry.png: ${message}`);
}

function pngDimensions(bytes) {
  if (bytes.length < 8 || !bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("does not start with the PNG signature");
  }
  if (bytes.length < 24) {
    fail("too short to hold an IHDR chunk");
  }
  const firstSize = bytes.readUInt32BE(8);
  const firstType = bytes.toString("latin1", 12, 16);
  if (firstSize !== 13 || firstType !== "IHDR") {
    fail("first chunk is not a 13-byte IHDR");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width > MAX_EDGE || height > MAX_EDGE) {
    fail(`is ${width}x${height}, over the ${MAX_EDGE}x${MAX_EDGE} limit`);
  }
  if (bytes.length > MAX_BYTES) {
    fail(`is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  return { width, height };
}

function main() {
  const bytes = readFileSync(source);
  const { width, height } = pngDimensions(bytes);
  mkdirSync(outDir, { recursive: true });
  writeFileSync(target, bytes);
  if (!readFileSync(target).equals(bytes)) {
    fail("read-back of the written file differs from the source");
  }
  console.log(`wrote ${target}: ${width}x${height} PNG, ${bytes.length} bytes`);
}

main();
