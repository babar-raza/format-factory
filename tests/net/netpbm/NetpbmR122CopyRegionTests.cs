// Tests for NetpbmImage.CopyRegion() and Clone() accessed via NetpbmDocument.Image.
// Sprint: FORMAT-FACTORY-NETPBM-COPY-REGION-20260626
// Ledger: R122-GOVERNED-DOTNET-NETPBM-COPY-REGION-001

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Netpbm.Tests;

/// <summary>
/// R122: CopyRegion(source, srcTop, srcLeft, h, w, destTop, destLeft) — copies
/// a rectangular region from source image into this image at the destination.
/// Clone() — creates an independent copy of the image.
/// Tests use PGM for simplicity, verified via GetPixel after operation.
/// </summary>
public class NetpbmR122CopyRegionTests
{
    private static NetpbmDocument LoadPgm(string content)
    {
        var bytes = Encoding.ASCII.GetBytes(content);
        using var ms = new MemoryStream(bytes);
        return NetpbmDocument.LoadStream(ms);
    }

    // ---- Clone: independent copy ----

    [Fact]
    public void Clone_CreatesIndependentCopy_DimensionsMatch()
    {
        const string pgm = "P2\n3 2\n255\n10 20 30\n40 50 60\n";
        var doc = LoadPgm(pgm);
        var cloned = doc.Image.Clone();

        Assert.Equal(doc.Width, cloned.Width);
        Assert.Equal(doc.Height, cloned.Height);
        Assert.Equal(doc.Format, cloned.Format);
    }

    [Fact]
    public void Clone_Pixels_MatchOriginal()
    {
        const string pgm = "P2\n2 2\n255\n10 20\n30 40\n";
        var doc = LoadPgm(pgm);
        var cloned = doc.Image.Clone();

        var clonedDoc = NetpbmDocument.FromImage(cloned);
        Assert.Equal(doc.GetPixel(0, 0), clonedDoc.GetPixel(0, 0));
        Assert.Equal(doc.GetPixel(0, 1), clonedDoc.GetPixel(0, 1));
        Assert.Equal(doc.GetPixel(1, 0), clonedDoc.GetPixel(1, 0));
        Assert.Equal(doc.GetPixel(1, 1), clonedDoc.GetPixel(1, 1));
    }

    [Fact]
    public void Clone_MutationIndependent_OriginalUnchanged()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);
        var cloned = doc.Image.Clone();

        // Mutate clone; original should be unaffected
        cloned.SetPixel(0, 0, 255);

        Assert.Equal(0, doc.GetPixel(0, 0)); // original unchanged
    }

    // ---- CopyRegion: basic copy ----

    [Fact]
    public void CopyRegion_Pgm_CopiesPixelsToDestination()
    {
        // Source: 4×4 with a filled region at (1,1) to (2,2)
        const string src = "P2\n4 4\n255\n0 0 0 0\n0 100 100 0\n0 100 100 0\n0 0 0 0\n";
        // Dest: 4×4 all zeros
        const string dst = "P2\n4 4\n255\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";

        var srcDoc = LoadPgm(src);
        var dstDoc = LoadPgm(dst);

        // Copy the 2×2 region at (1,1) from src to (0,0) in dst
        dstDoc.Image.CopyRegion(srcDoc.Image, 1, 1, 2, 2, 0, 0);

        Assert.Equal(100, dstDoc.GetPixel(0, 0));
        Assert.Equal(100, dstDoc.GetPixel(0, 1));
        Assert.Equal(100, dstDoc.GetPixel(1, 0));
        Assert.Equal(100, dstDoc.GetPixel(1, 1));
        // Pixels outside destination region unchanged
        Assert.Equal(0, dstDoc.GetPixel(2, 0));
        Assert.Equal(0, dstDoc.GetPixel(0, 2));
    }

    [Fact]
    public void CopyRegion_Pgm_SourceAndDestinationDistinct()
    {
        // Clone + CopyRegion: verify source not modified
        const string pgm = "P2\n3 3\n255\n1 2 3\n4 5 6\n7 8 9\n";
        var src = LoadPgm(pgm);
        var dst = LoadPgm("P2\n3 3\n255\n0 0 0\n0 0 0\n0 0 0\n");

        dst.Image.CopyRegion(src.Image, 0, 0, 3, 3, 0, 0);

        // Verify all 9 pixels copied correctly
        for (int row = 0; row < 3; row++)
            for (int col = 0; col < 3; col++)
                Assert.Equal(src.GetPixel(row, col), dst.GetPixel(row, col));
    }

    // ---- CopyRegion: null source throws ----

    [Fact]
    public void CopyRegion_NullSource_Throws()
    {
        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var doc = LoadPgm(pgm);
        Assert.Throws<ArgumentNullException>(() =>
            doc.Image.CopyRegion(null!, 0, 0, 2, 2, 0, 0));
    }

    // ---- CopyRegion: format mismatch throws ----

    [Fact]
    public void CopyRegion_FormatMismatch_Throws()
    {
        var srcBytes = Encoding.ASCII.GetBytes("P3\n2 2\n255\n0 0 0  0 0 0\n0 0 0  0 0 0\n");
        using var ms = new MemoryStream(srcBytes);
        var ppmDoc = NetpbmDocument.LoadStream(ms);

        const string pgm = "P2\n2 2\n255\n0 0\n0 0\n";
        var pgmDoc = LoadPgm(pgm);

        Assert.Throws<ArgumentException>(() =>
            pgmDoc.Image.CopyRegion(ppmDoc.Image, 0, 0, 2, 2, 0, 0));
    }

    // ---- Dogfood pipeline: Clone → edit clone → CopyRegion back ----

    [Fact]
    public void DogfoodPipeline_CloneEditCopyBack_VerifyResult()
    {
        const string pgm = "P2\n4 4\n255\n0 0 0 0\n0 0 0 0\n0 0 0 0\n0 0 0 0\n";
        var original = LoadPgm(pgm);

        // Clone and edit the clone
        var edited = original.Image.Clone();
        edited.FillRegion(0, 0, 2, 2, value: 77); // fill top-left quadrant

        // Copy the edited top-left back to original bottom-right
        original.Image.CopyRegion(edited, 0, 0, 2, 2, 2, 2);

        // Bottom-right 2×2 of original should now be 77
        Assert.Equal(77, original.GetPixel(2, 2));
        Assert.Equal(77, original.GetPixel(2, 3));
        Assert.Equal(77, original.GetPixel(3, 2));
        Assert.Equal(77, original.GetPixel(3, 3));

        // Top-left of original should still be 0
        Assert.Equal(0, original.GetPixel(0, 0));
    }
}
