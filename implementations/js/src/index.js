import fs from "fs";
import p from "path";
import pkg from "pngjs";
const { PNG } = pkg;

import { openGroup, NestedArray, slice } from "zarr";
import FSStore from "./fsstore.js";

const CHUNKS = [100, 100, 1];
const STR_TO_COMPRESSOR = {
  gzip: { id: "gzip", level: 1 },
  blosc: { id: "blosc", cname: "lz4", clevel: 5, blocksize: 0, shuffle: 1 },
  zlib: { id: "zlib", level: 1 },
};

// Simple convenience method to init the root for an empty store.
async function open(path) {
  const store = new FSStore(path);
  const text = JSON.stringify({ zarr_format: 2 });
  await store.setItem(".zgroup", Buffer.from(text));
  return openGroup(store);
}

function imread(path) {
  const buf = fs.readFileSync(path);
  const { data, height, width } = PNG.sync.read(buf, { colorType: 2 });
  const arr = new NestedArray(new Uint8Array(data), [height, width, 4]);
  return arr.get([null, null, slice(3)]); // drop alpha channel
}

function getName(config) {
  if (config === null) return "raw";
  if (config.cname) return `${config.id}/${config.cname}`;
  return config.id;
}

async function generateZarrFormat(codecIds = ["gzip", "blosc", "zlib", null]) {
  const path = p.join("..", "..", "data", "js.zr");
  const img = imread(p.join("..", "..", "data", "reference_image.png"));

  if (fs.existsSync(path)) {
    fs.rmdirSync(path, { recursive: true, force: true });
  }

  const grp = await open(path);
  for (const id of codecIds) {
    const config = id ? STR_TO_COMPRESSOR[id] : null;
    const name = getName(config);
    grp.createDataset(name, undefined, img, {
      compressor: config,
      chunks: CHUNKS,
      fillValue: 0,
    });
  }
}

generateZarrFormat();
