package zarr_implementations.jzarr;

import com.bc.zarr.ArrayParams;
import com.bc.zarr.CompressorFactory;
import com.bc.zarr.DataType;
import com.bc.zarr.ZarrArray;
import com.bc.zarr.ZarrGroup;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.io.File;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;


public class App {

    enum Compression {
        raw("null"),
        zlib("zlib"),
        blosc("blosc");

        private final String value;

        private Compression(final String value) {
            this.value = value;
        }

        @Override
        public String toString() {
            return value;
        }
    }

    // NOTE for now we use 100, 100, 1 as block-size in all examples
    // maybe it's a better idea to make this more irregular though
    private static final int[] CHUNKS = new int[]{1, 100, 100};
    private static final int[] SHAPE = new int[] {3, 512, 512};
    private static final Path IN_PATH = Paths.get("..", "..", "data", "reference_image.png");
    private static final Path OUT_PATH = Paths.get("..", "..", "data", "jzarr_flat.zr");

    private static byte[] getData() throws IOException {

        final BufferedImage bufferedImage = ImageIO.read(new File(IN_PATH.toString()));
        byte[] pixels = ((DataBufferByte) bufferedImage.getRaster().getDataBuffer()).getData();
        return pixels;
    }

    public static void main(String args[]) throws Exception {
        byte[] data = getData();

        final ZarrGroup container = ZarrGroup.create(OUT_PATH);
        for (final Compression compressionType : Compression.values()) {
            ArrayParams arrayParams = new ArrayParams()
                .shape(SHAPE)
                .chunks(CHUNKS)
                .dataType(DataType.u2)
                // .nested(nested) FIXME: requires a different branch
                .compressor(CompressorFactory.create(compressionType.toString()));

            Path subdir = OUT_PATH.resolve(compressionType.toString());
            ZarrArray zArray = ZarrArray.create(subdir, arrayParams);
            // final ZarrArray zarr = ZarrArray.open(getRootPath().resolve(pathName));
            zArray.write(data, SHAPE, new int[]{0, 0, 0});
        }
    }
}
