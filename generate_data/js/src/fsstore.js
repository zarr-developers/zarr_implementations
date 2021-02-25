import path from "path";
import { promises as fsp } from "fs";
import fs from "fs";

import { KeyError } from "zarr";

class FSStore {
  constructor(root) {
    this.root = root;
    if (!fs.existsSync(root)) {
      fs.mkdirSync(root, { recursive: true });
    }
  }

  getItem(key) {
    const fp = path.join(this.root, key);
    return fsp.readFile(fp, null).catch((err) => {
      if (err.code === "ENOENT") {
        throw new KeyError(key);
      }
      throw err;
    });
  }

  async setItem(key, value) {
    const fp = path.join(this.root, key);
    await fsp.mkdir(path.dirname(fp), { recursive: true });
    await fsp.writeFile(fp, Buffer.from(value), null);
  }

  containsItem(key) {
    const fp = path.join(this.root, key);
    return fs.existsSync(fp);
  }
}

export default FSStore;
