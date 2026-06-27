// Tests for ZstDocument.GetMultiFrameCount, SkipToFrame, GetFrameOffset deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-ZST-R243

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R243: Tests for ZstDocument.GetMultiFrameCount, SkipToFrame, GetFrameOffset deeper.
/// GetMultiFrameCount(): returns the number of independently decompressible frames in the file.
/// SkipToFrame(frameIndex): positions the reader at the start of the given frame.
/// GetFrameOffset(frameIndex): returns the byte offset of the specified frame within the file.
/// Covers: GetMultiFrameCount no-throw; GetMultiFrameCount positive; GetMultiFrameCount consistent;
/// GetMultiFrameCount save-load;
/// SkipToFrame no-throw; SkipToFrame consistent;
/// GetFrameOffset no-throw; GetFrameOffset non-negative; GetFrameOffset consistent;
/// GetFrameOffset save-load;
/// dogfood Compress→GetMultiFrameCount→SkipToFrame→GetFrameOffset→SaveToFile pipeline.
/// </summary>
public class ZstR243GetMultiFrameCountAndSkipFrameDeepTests : IDisposable
{
    private readonly string _tempDir;

    public ZstR243GetMultiFrameCountAndSkipFrameDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "ZstR243_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateMultiFrameZst()
    {
        var content = string.Join("\n", System.Linq.Enumerable.Repeat(
            "MULTI_FRAME_TEST_ALPHA_BETA_GAMMA_DELTA_EPSILON_ZETA_ETA_THETA_IOTA_KAPPA_LAMBDA_MU", 120));
        var data = ZstWriter.Compress(Encoding.UTF8.GetBytes(content));
        var path = TempFile("multiframe.zst");
        File.WriteAllBytes(path, data);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetMultiFrameCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetMultiFrameCount_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var ex = Record.Exception(() => doc.GetMultiFrameCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetMultiFrameCount_Positive()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        Assert.True(doc.GetMultiFrameCount() > 0);
    }

    [Fact]
    public void GetMultiFrameCount_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        Assert.Equal(doc.GetMultiFrameCount(), doc.GetMultiFrameCount());
    }

    [Fact]
    public void GetMultiFrameCount_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var before = doc.GetMultiFrameCount();
        var path = TempFile("mfc_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetMultiFrameCount());
    }

    // -------------------------------------------------------------------------
    // SkipToFrame
    // -------------------------------------------------------------------------

    [Fact]
    public void SkipToFrame_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var ex = Record.Exception(() => doc.SkipToFrame(0));
        Assert.Null(ex);
    }

    [Fact]
    public void SkipToFrame_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var ex1 = Record.Exception(() => doc.SkipToFrame(0));
        var ex2 = Record.Exception(() => doc.SkipToFrame(0));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }

    // -------------------------------------------------------------------------
    // GetFrameOffset
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFrameOffset_NoThrow()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var ex = Record.Exception(() => doc.GetFrameOffset(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFrameOffset_NonNegative()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        Assert.True(doc.GetFrameOffset(0) >= 0);
    }

    [Fact]
    public void GetFrameOffset_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        Assert.Equal(doc.GetFrameOffset(0), doc.GetFrameOffset(0));
    }

    [Fact]
    public void GetFrameOffset_SaveLoad_Consistent()
    {
        var doc = ZstDocument.LoadFile(CreateMultiFrameZst());
        var before = doc.GetFrameOffset(0);
        var path = TempFile("fo_save.zst");
        doc.SaveToFile(path);
        var loaded = ZstDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFrameOffset(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetMultiFrameCount_SkipToFrame_GetFrameOffset_SaveToFile_Pipeline()
    {
        // Digital humanities — corpus linguistics compressed text archive (multi-document batch)
        var sb = new StringBuilder();
        sb.AppendLine("doc_id,author,era,genre,word_count,sentence_count,avg_sentence_length,type_token_ratio,hapax_ratio");
        string[] eras = { "Early_Modern", "Restoration", "Augustan", "Romantic", "Victorian", "Edwardian" };
        string[] genres = { "Novel", "Drama", "Poetry", "Pamphlet", "Sermon", "Essay", "Letter" };
        var rng = new Random(20241001);
        for (int i = 0; i < 450; i++)
        {
            var era = eras[i % 6];
            var genre = genres[i % 7];
            int wc = 500 + rng.Next(0, 50000);
            int sc = wc / (8 + rng.Next(0, 12));
            double asl = (double)wc / sc;
            double ttr = 0.3 + rng.NextDouble() * 0.4;
            double hapax = ttr * (0.4 + rng.NextDouble() * 0.3);
            sb.AppendLine($"DOC{i:D5},{$"Author_{(i % 30):D3}"},{ era},{genre},{wc},{sc},{asl:F1},{ttr:F3},{hapax:F3}");
        }
        var raw = Encoding.UTF8.GetBytes(sb.ToString());
        var compressed = ZstWriter.Compress(raw);
        var path = TempFile("dogfood_corpus.zst");
        File.WriteAllBytes(path, compressed);

        var doc = ZstDocument.LoadFile(path);
        Assert.True(doc.CompressedSize > 0);
        Assert.True(doc.DecompressedSize > 0);

        // GetMultiFrameCount
        var frameCount = doc.GetMultiFrameCount();
        Assert.True(frameCount > 0);
        Assert.Equal(frameCount, doc.GetMultiFrameCount()); // consistent

        // SkipToFrame
        var skipEx = Record.Exception(() => doc.SkipToFrame(0));
        Assert.Null(skipEx);

        // GetFrameOffset
        var offset0 = doc.GetFrameOffset(0);
        Assert.True(offset0 >= 0);
        Assert.Equal(offset0, doc.GetFrameOffset(0)); // consistent

        // SaveToFile
        var out1 = TempFile("dogfood_corpus_out.zst");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));

        // LoadFile — verify frame metadata preserved
        var loaded = ZstDocument.LoadFile(out1);
        Assert.Equal(frameCount, loaded.GetMultiFrameCount());
        Assert.Equal(offset0, loaded.GetFrameOffset(0));

        // Decompression round-trip
        var decompressed = loaded.Decompress();
        Assert.NotNull(decompressed);
        var text = Encoding.UTF8.GetString(decompressed);
        Assert.Contains("Early_Modern", text);
        Assert.Contains("Victorian", text);
        Assert.Contains("Novel", text);

        // ValidateChecksum
        Assert.True(doc.ValidateChecksum());

        // GetWindowSize
        Assert.True(doc.GetWindowSize() > 0);

        // Second compression
        var recompressed = ZstWriter.Compress(decompressed);
        var out2 = TempFile("dogfood_corpus_v2.zst");
        File.WriteAllBytes(out2, recompressed);
        var loaded2 = ZstDocument.LoadFile(out2);
        Assert.True(loaded2.GetMultiFrameCount() > 0);
        Assert.True(loaded2.GetFrameOffset(0) >= 0);
        Assert.Equal(0xFD2FB528u, (uint)loaded2.GetMagicNumber());
    }
}
