import net.imglib2.RandomAccessibleInterval;
import net.imglib2.img.array.ArrayImgs;
import net.imglib2.type.numeric.integer.UnsignedByteType;
import net.imglib2.util.Intervals;
import net.imglib2.view.Views;
import org.janelia.saalfeldlab.n5.Bzip2Compression;
import org.janelia.saalfeldlab.n5.Compression;
import org.janelia.saalfeldlab.n5.DataType;
import org.janelia.saalfeldlab.n5.DatasetAttributes;
import org.janelia.saalfeldlab.n5.GzipCompression;
import org.janelia.saalfeldlab.n5.Lz4Compression;
import org.janelia.saalfeldlab.n5.N5FSWriter;
import org.janelia.saalfeldlab.n5.RawCompression;
import org.janelia.saalfeldlab.n5.XzCompression;
import org.janelia.saalfeldlab.n5.imglib2.N5Utils;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.awt.image.DataBufferByte;
import java.io.File;
import java.io.IOException;
import java.nio.file.Paths;


public class App {

    // NOTE for now we use 100, 100, 1 as block-size in all examples
    // maybe it's a better idea to make this more irregular though
	private static final int[] BLOCK_SIZE = new int[]{100, 100, 1};
	private static final String IN_PATH = Paths.get("..", "..", "data", "reference_image.png").toString();
	private static final String OUT_PATH = Paths.get("..", "..", "data", "n5-java.n5").toString();

	private static Compression[] getCompressions() {

		return new Compression[] {
				new RawCompression(),
				new Bzip2Compression(),
				new GzipCompression(),
				new Lz4Compression(),
				new XzCompression()
		};
	}

	private static RandomAccessibleInterval<UnsignedByteType> getData() throws IOException {

		final BufferedImage bufferedImage = ImageIO.read(new File(IN_PATH));
		byte[] pixels = ((DataBufferByte) bufferedImage.getRaster().getDataBuffer()).getData();
		// some annoying axis manipulations because of how the image is read
		return Views.zeroMin(Views.moveAxis(
				Views.invertAxis(ArrayImgs.unsignedBytes(
					pixels,
					pixels.length / bufferedImage.getWidth() / bufferedImage.getHeight(),
					bufferedImage.getWidth(),
					bufferedImage.getHeight()), 0),
				0,
				2));
	}


	public static void main(String args[]) throws IOException {
		RandomAccessibleInterval<UnsignedByteType> data = getData();
		final N5FSWriter container = new N5FSWriter(OUT_PATH);
		for (final Compression compression : getCompressions()) {
			final DatasetAttributes attrs = new DatasetAttributes(Intervals.dimensionsAsLongArray(data), BLOCK_SIZE, DataType.UINT8, compression);
			final String dataset = compression.getType();
			container.createDataset(dataset, attrs);
			N5Utils.save(data, container, dataset, BLOCK_SIZE, compression);
		}
	}

}
