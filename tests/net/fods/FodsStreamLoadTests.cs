// Tests for FodsDocument.Load(Stream) overload (QF-3-002, PQ-008)

using System;
using System.IO;
using FormatFactory.Fods;
using Xunit;

namespace FormatFactory.Fods.Tests;

public class FodsStreamLoadTests
{
    private static readonly string SamplesDir = Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory,
            "../../../../../../samples/by-format/fods"));

    private static string SampleFodsPath =>
        Path.Combine(SamplesDir, "minimal-spreadsheet.fods");

    [Fact]
    public void Load_Stream_LoadsDocument()
    {
        using var stream = File.OpenRead(SampleFodsPath);
        var doc = FodsDocument.Load(stream);
        Assert.NotNull(doc);
        Assert.True(doc.SheetCount >= 1);
    }

    [Fact]
    public void Load_Stream_ProducesSameSheetCount_AsFileLoad()
    {
        var fileDoc = FodsDocument.Load(SampleFodsPath);
        using var stream = File.OpenRead(SampleFodsPath);
        var streamDoc = FodsDocument.Load(stream);
        Assert.Equal(fileDoc.SheetCount, streamDoc.SheetCount);
    }

    [Fact]
    public void Load_Stream_MemoryStream_Works()
    {
        byte[] bytes = File.ReadAllBytes(SampleFodsPath);
        using var ms = new MemoryStream(bytes);
        var doc = FodsDocument.Load(ms);
        Assert.NotNull(doc);
        Assert.True(doc.SheetCount >= 1);
    }

    [Fact]
    public void Load_NullStream_Throws_ArgumentNullException()
    {
        Assert.Throws<ArgumentNullException>(() => FodsDocument.Load((Stream)null!));
    }

    [Fact]
    public void Load_Stream_SheetNames_Match_FileLoad()
    {
        var fileDoc = FodsDocument.Load(SampleFodsPath);
        using var stream = File.OpenRead(SampleFodsPath);
        var streamDoc = FodsDocument.Load(stream);
        Assert.Equal(fileDoc.GetSheetNames(), streamDoc.GetSheetNames());
    }
}
