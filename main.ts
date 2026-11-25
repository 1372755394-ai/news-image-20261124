// news-image-20261124 — the program that delivers the entry.
//
// build_frontpage.py renders the finished front page for Tuesday
// 24 November 2026 into entry.png (1024x1024): Iran's vow to fight
// the US naval blockade, the Zaporizhzhia strike, the Gaza strikes,
// the Ras Al Khaimah bus crash, Russian jets in South Korea's air
// zone, NATO's space warning and Germany's Delta deal. This file
// only carries that page to the grader: it reads the PNG, confirms
// it is a real PNG inside the competition's limits, and writes the
// very same bytes to $MAKEFUN_OUTPUT_DIR/entry.png, falling back to
// /output/entry.png. Node 22, standard library only, no network,
// no secrets, and the same bytes out on every run.

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const TARGET_NAME = "entry.png";
const BYTE_LIMIT = 1_000_000;
const EDGE_LIMIT = 1024;
const MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

const folder = dirname(fileURLToPath(import.meta.url));
const origin = join(folder, TARGET_NAME);
const outFolder = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const destination = join(outFolder, TARGET_NAME);

function refuse(why) {
  throw new Error(`entry.png: ${why}`);
}

function inspectPng(bytes) {
  if (bytes.length < 8 || !bytes.subarray(0, 8).equals(MAGIC)) {
    refuse("does not start with the PNG signature");
  }
  if (bytes.length < 24) {
    refuse("too short to hold an IHDR chunk");
  }
  const chunkSize = bytes.readUInt32BE(8);
  const chunkKind = bytes.toString("latin1", 12, 16);
  if (chunkSize !== 13 || chunkKind !== "IHDR") {
    refuse("first chunk is not a 13-byte IHDR");
  }
  const wide = bytes.readUInt32BE(16);
  const tall = bytes.readUInt32BE(20);
  if (wide > EDGE_LIMIT || tall > EDGE_LIMIT) {
    refuse(`is ${wide}x${tall}, over the ${EDGE_LIMIT}x${EDGE_LIMIT} limit`);
  }
  if (bytes.length > BYTE_LIMIT) {
    refuse(`is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  const tail = bytes.subarray(bytes.length - 12);
  if (tail.readUInt32BE(0) !== 0 || tail.toString("latin1", 4, 8) !== "IEND") {
    refuse("does not end with an IEND chunk");
  }
  return { wide, tall };
}

function deliver() {
  const bytes = readFileSync(origin);
  const { wide, tall } = inspectPng(bytes);
  mkdirSync(outFolder, { recursive: true });
  writeFileSync(destination, bytes);
  const written = readFileSync(destination);
  if (!written.equals(bytes)) {
    refuse("read-back of the written file differs from the source");
  }
  console.log(`wrote ${destination}: ${wide}x${tall} PNG, ${bytes.length} bytes`);
}

deliver();
