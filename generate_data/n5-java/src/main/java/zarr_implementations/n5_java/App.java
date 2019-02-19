package zarr_implementations.n5_java;

import org.janelia.saalfeldlab.n5.*;

import java.io.IOException;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.File;
import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.awt.image.Raster;


public class App {

    static private long[] dimensions = new long[]{512, 512, 3};
    static private int[] blockSize = new int[]{100, 100, 1};
    static private int[] nBlocks = new int[]{6, 6, 3};

    static private String inPath = "../../data/reference_image.png";
	static private String outPath = "../../data/n5-java.n5";

    // NOTE this needs to be int because that's what we get by imageio's
    // getSamples
    static int[] dataBlock;
	
    private static Compression[] getCompressions() {

		return new Compression[] {
				new RawCompression(),
				new Bzip2Compression(),
				new GzipCompression(),
				new Lz4Compression(),
				new XzCompression()
			};
	}

    static private N5Writer n5;
    
    public static void makeTestData(Compression compression) throws IOException {
        
        final String compressionName = compression.getType();
		
        // open the n5 filesystem writer and create the dataset
		n5 = new N5FSWriter(outPath);
        // TODO we want uint8 in the end !
        n5.createDataset(compressionName, dimensions, blockSize, DataType.INT32, compression);
        final DatasetAttributes attrs = n5.getDatasetAttributes(compressionName);

        // read the input image
        File initialImage = new File(inPath);
        BufferedImage bImage = ImageIO.read(initialImage);
        Raster image = bImage.getData();
        
        dataBlock = new int[blockSize[0] * blockSize[1] * blockSize[2]];
        
        // iterate over all image blocks
        for(int x = 0; x < nBlocks[0]; x++) {
            for(int y = 0; y < nBlocks[1]; y++) {
                for(int c = 0; c < nBlocks[2]; c++) {
                    // TODO calculate proper height and width for edge chunks
                    int w = blockSize[0];
                    int h = blockSize[1];
                    // read the pixels TODO is this ok ??
                    dataBlock = image.getSamples(x, y, w, h, c, dataBlock);
                    
                    // write byte
                    final IntArrayDataBlock intDataBlock = new IntArrayDataBlock(
                        blockSize, new long[]{x, y, c}, dataBlock
                    );
                    n5.writeBlock(compressionName, attrs, intDataBlock);
                }
            }
        }
    }
    

    public static void main(String args[]) throws IOException {
		for (final Compression compression : getCompressions()) {
            makeTestData(compression);
        }
    }

}
