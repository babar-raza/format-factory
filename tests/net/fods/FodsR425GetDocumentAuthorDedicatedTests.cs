// Tests for FodsDocument.GetDocumentAuthor dedicated coverage.
// Sprint: ff-sprint-s382-dotnet-deepening-20260630
// Ledger: PC-FODS-R425

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// R425: Dedicated tests for FodsDocument.GetDocumentAuthor().
/// New document returns non-null.
/// SheetCount unchanged after GetDocumentAuthor.
/// Idempotent (called twice same result).
/// Returns string type.
/// Dogfood: SetDocumentAuthor Jane Smith then Get.
/// Dogfood: SetDocumentAuthor Corporate Legal Dept then Get.
/// Dogfood: Set empty string then Get.
/// Dogfood: multiple Set+Get round-trips.
/// </summary>
public class FodsR425GetDocumentAuthorDedicatedTests
{
    // -------------------------------------------------------------------------
    // Functional tests
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDocumentAuthor_NewDocument_ReturnsNonNull()
    {
        var doc = FodsDocument.CreateNew();
        string author = doc.GetDocumentAuthor();
        Assert.NotNull(author);
    }

    [Fact]
    public void GetDocumentAuthor_SheetCountUnchanged()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        int before = doc.SheetCount;
        _ = doc.GetDocumentAuthor();
        Assert.Equal(before, doc.SheetCount);
    }

    [Fact]
    public void GetDocumentAuthor_Idempotent()
    {
        var doc = FodsDocument.CreateNew();
        string first = doc.GetDocumentAuthor();
        string second = doc.GetDocumentAuthor();
        Assert.Equal(first, second);
    }

    [Fact]
    public void GetDocumentAuthor_ReturnsStringType()
    {
        var doc = FodsDocument.CreateNew();
        object author = doc.GetDocumentAuthor();
        Assert.IsType<string>(author);
    }

    // -------------------------------------------------------------------------
    // Dogfood pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_SetAuthorJaneSmithThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentAuthor("Jane Smith");
        string author = doc.GetDocumentAuthor();
        Assert.Equal("Jane Smith", author);
    }

    [Fact]
    public void DogfoodPipeline_SetAuthorCorporateLegalDeptThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentAuthor("Corporate Legal Dept");
        string author = doc.GetDocumentAuthor();
        Assert.Equal("Corporate Legal Dept", author);
    }

    [Fact]
    public void DogfoodPipeline_SetEmptyStringThenGet()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentAuthor("");
        string author = doc.GetDocumentAuthor();
        Assert.Equal("", author);
    }

    [Fact]
    public void DogfoodPipeline_MultipleSetGetRoundTrips()
    {
        var doc = FodsDocument.CreateNew();
        doc.SetDocumentAuthor("Alice");
        Assert.Equal("Alice", doc.GetDocumentAuthor());
        doc.SetDocumentAuthor("Bob");
        Assert.Equal("Bob", doc.GetDocumentAuthor());
        doc.SetDocumentAuthor("Charlie");
        Assert.Equal("Charlie", doc.GetDocumentAuthor());
    }
}
