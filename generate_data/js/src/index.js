import fs from "fs";
import p from "path";
import { PNG } from "pngjs";

import { openGroup, NestedArray, slice } from "zarr";
import FSStore from "./fsstore.js";

const CHUNKS = [100, 100, 1];
const STR_TO_COMPRESSOR = {
  gzip: { id: "gzip" },
  blosc: { id: "blosc", cname: "lz4" },
  zlib: { id: "zlib" },
};

// Simple convenience method to init the root for an empty store.
async function open(path) {
  const store = new FSStore(path);
  const text = JSON.stringify({ zarr_format: 2 });
  await store.setItem(".zgroup", Buffer.from(text))
  return openGroup(store);
}

function getImage(path) {
  const buf = fs.readFileSync(path);
  const { data, height, width } = PNG.sync.read(buf, { colorType: 2 });
  const arr = new NestedArray(new Uint8Array(data), [height, width, 4]);
  return arr.get([null, null, slice(3)]); // drop alpha channel
}

function getName(config) {
    if (config === null) return 'raw';
    if (config.cname) return `${config.id}/${config.cname}`;
    return config.id;
}

async function generateZarrFormat(codecIds = ["gzip", "blosc", "zlib", null]) {
  const path = p.join("..", "..", "data", "js.zr");
  const img = getImage(p.join("..", "..", "data", "reference_image.png"));

  fs.rmdirSync(path, { recursive: true, force: true });
  const grp = await open(path);
  for (const id of codecIds) {
    const config = id ? STR_TO_COMPRESSOR[id] : null;
    const name = getName(config);
    grp.createDataset(name, undefined, img, {
      compressor: config,
      chunks: CHUNKS,
    });
  }
}

generateZarrFormat();
