package zarr_implementations.jzarr;


import com.bc.zarr.ArrayParams;
import com.bc.zarr.CompressorFactory;
import com.bc.zarr.DataType;
import com.bc.zarr.ZarrArray;
import com.bc.zarr.ZarrGroup;

import javax.imageio.ImageIO;
import java.awt.*;
import java.awt.image.BufferedImage;
import java.awt.image.DataBuffer;
import java.awt.image.DataBufferByte;
import java.awt.image.DataBufferInt;
import java.awt.image.WritableRaster;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.stream.IntStream;


public class App {

    enum Compression {
        raw("null"),
        zlib("zlib");

        private final String value;

        Compression(final String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return value;
        }
    }

    // NOTE for now we use 100, 100, 1 as block-size in all examples
    // maybe it's a better idea to make this more irregular though
    private static final int WIDTH = 512;
    private static final int HEIGHT = 512;
    private static final int CHANNELS = 3;
    private static final int[] CHUNKS = new int[]{100, 100, 1};
    private static final int[] SHAPE = new int[] {WIDTH, HEIGHT, CHANNELS};
    //    private static final Path IN_PATH = Paths.get("..", "..", "data", "reference_image.png");
    private static final Path OUT_PATH = Paths.get("..", "..", "data", "jzarr_flat.zr");

    private static int[] getTestData() throws IOException {
        final BufferedImage image = ImageIO.read(new File("data/reference_image.png"));
        int[] result = new int[WIDTH * HEIGHT * CHANNELS];
        for (int i = 0; i < WIDTH; i++) {
            for (int j = 0; j < HEIGHT; j++) {
                Color color = new Color(image.getRGB(i, j));
                int index = (WIDTH*3*j) + (3*i);
                result[index] = color.getRed();
                result[index + 1] = color.getGreen();
                result[index + 2] = color.getBlue();
            }
        }
        return result;
    }


    private static int[] getArrayData(ZarrArray zarr) throws Exception {
        int[] data = new int[WIDTH * HEIGHT * CHANNELS];
        zarr.read(data, SHAPE, new int[]{0, 0, 0});
        int[] unsigned = new int[data.length];
        for (int i = 0; i < data.length; i++) {
            unsigned[i] = data[i] & 0xff;
        }
        return unsigned;
    }

    public static void main(String[] args) throws Exception {

        if (args.length != 0 && args.length != 3) {
            System.out.println("usage: App");
            System.out.println("usage: App -verify fpath dsname");
            System.exit(2);  // EARLY EXIT
        } else if (args.length == 3) {
            String fpath = args[1];
            String dsname = args[2];
            ZarrArray verification = ZarrGroup.open(fpath).openArray(dsname);
            int[] shape = verification.getShape();
            if (!Arrays.equals(SHAPE, shape)) {
                throw new RuntimeException(String.format(
                        "shape-mismatch expected:%s found:%s",
                        Arrays.toString(SHAPE), Arrays.toString(shape)
                ));
            }

            int[] test = getTestData();
            int[] verify = getArrayData(verification);
            if (!Arrays.equals(test, verify)) {
                throw new RuntimeException("values don't match");
            }
            return;  // EARLY EXIT
        }

        int[] data = getTestData();

        final ZarrGroup container = ZarrGroup.create(OUT_PATH);
        for (final Compression compressionType : Compression.values()) {
            ArrayParams arrayParams = new ArrayParams()
                    .shape(SHAPE)
                    .chunks(CHUNKS)
                    .dataType(DataType.u1)
                    // .nested(nested) FIXME: requires a different branch
                    .compressor(CompressorFactory.create(compressionType.toString()));  // jzarr name, "null"

            String dsname = compressionType.name(); // zarr_implementation name, "raw"

            if ("blosc".equals(dsname)) {
                dsname = "blosc/lz4"; // FIXME: better workaround?
            }

            Path subdir = OUT_PATH.resolve(dsname);
            ZarrArray zArray = ZarrArray.create(subdir, arrayParams);
            // final ZarrArray zarr = ZarrArray.open(getRootPath().resolve(pathName));
            zArray.write(data, SHAPE, new int[]{0, 0, 0});
        }
    }
}
