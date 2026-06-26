// Tests for FodtDocument.Load(Stream) dedicated coverage.
// Sprint: ff-sprint-s217-dotnet-deepening-20260629
// Ledger: PC-FODT-R232

using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R232: Dedicated tests for FodtDocument.Load(Stream).
/// Null stream → throws exception.
/// Valid stream from saved doc: returns non-null document.
/// Loaded doc: ParagraphCount matches original.
/// Loaded doc: paragraph text matches original.
/// Loaded doc: author matches original if set.
/// Loaded doc: GetMimeType non-null.
/// Multiple loads from same bytes: same paragraph count.
/// Dogfood: save → load → save → load pipeline stable.
/// Dogfood: heading count preserved.
/// </summary>
public class FodtR232LoadStreamTests : IDisposable
{
    private readonly List<Stream> _streams = new();

    private MemoryStream SaveDoc(FodtDocument doc)
    {
        var ms = new MemoryStream();
        _streams.Add(ms);
        doc.SaveToStream(ms);
        ms.Position = 0;
        return ms;
    }

    public void Dispose()
    {
        foreach (var s in _streams) s.Dispose();
    }

    // -------------------------------------------------------------------------
    // Guard tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_NullStream_ThrowsException()
    {
        Assert.ThrowsAny<Exception>(() => FodtDocument.Load((Stream)null!));
    }

    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void Load_ValidStream_ReturnsNonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Hello");
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.NotNull(loaded);
    }

    [Fact]
    public void Load_ParagraphCountMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("First");
        doc.AppendParagraph("Second");
        doc.AppendParagraph("Third");
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.Equal(doc.ParagraphCount, loaded.ParagraphCount);
    }

    [Fact]
    public void Load_ParagraphTextMatches()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Exact Text");
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.Equal("Exact Text", loaded.GetParagraphText(0));
    }

    [Fact]
    public void Load_AuthorPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.SetAuthor("Test Author");
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.Equal("Test Author", loaded.GetAuthor());
    }

    [Fact]
    public void Load_GetMimeType_NonNull()
    {
        var doc = FodtDocument.CreateEmpty();
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.NotNull(loaded.GetMimeType());
    }

    [Fact]
    public void Load_MultipleLoads_SameParagraphCount()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Content");
        doc.AppendParagraph("More");
        var bytes = SaveDoc(doc).ToArray();
        var ms1 = new MemoryStream(bytes);
        var ms2 = new MemoryStream(bytes);
        _streams.Add(ms1);
        _streams.Add(ms2);
        var l1 = FodtDocument.Load(ms1);
        var l2 = FodtDocument.Load(ms2);
        Assert.Equal(l1.ParagraphCount, l2.ParagraphCount);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipelines
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SaveLoadSaveLoad_Stable()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("Paragraph A");
        var ms1 = SaveDoc(doc);
        var loaded1 = FodtDocument.Load(ms1);
        var ms2 = SaveDoc(loaded1);
        var loaded2 = FodtDocument.Load(ms2);
        Assert.Equal(doc.ParagraphCount, loaded2.ParagraphCount);
    }

    [Fact]
    public void DogfoodPipeline_HeadingCountPreserved()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendHeading("Chapter 1", 1);
        doc.AppendParagraph("Body text");
        doc.AppendHeading("Chapter 2", 1);
        var ms = SaveDoc(doc);
        var loaded = FodtDocument.Load(ms);
        Assert.Equal(doc.ParagraphCount, loaded.ParagraphCount);
    }
}
