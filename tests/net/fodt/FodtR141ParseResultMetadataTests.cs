// Tests for FodtParseResult extended metadata: Title, Creator, Subject, InitialCreator.
// Sprint: FORMAT-FACTORY-FODT-R141-20260627
// Ledger: R141-GOVERNED-DOTNET-FODT-PARSE-RESULT-METADATA-001

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R141: Tests for FodtParseResult metadata fields that are sparsely covered:
/// Title (dc:title from office:meta), Creator (dc:creator), Subject (dc:subject),
/// InitialCreator (meta:initial-creator), FileSizeBytes, OdfVersion, MimeType.
/// The fodt-opaque-nodes.fodt fixture contains dc:title="Opaque Node Text Test".
/// The fodt-minimal-roundtrip.fodt fixture has no office:meta — fields are null.
/// Covers: title present, title absent=null, creator absent=null, subject absent=null,
/// initialCreator absent=null, odfVersion present, mimeType present, fileSizeBytes>0,
/// fileSizeBytes matches actual file size, dogfood multi-property consistency check.
/// </summary>
public class FodtR141ParseResultMetadataTests
{
    private static readonly string FixturesDir =
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "fodt", "Fixtures");

    private static string FixturePath(string name) =>
        Path.GetFullPath(Path.Combine(FixturesDir, name));

    private static FodtParseResult Parse(string fixture)
    {
        var parser = new FodtParser();
        return parser.Parse(FixturePath(fixture));
    }

    // -------------------------------------------------------------------------
    // Title field
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_OpaqueNodesFixture_TitleIsPresent()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Equal("Opaque Node Text Test", result.Title);
    }

    [Fact]
    public void Parse_MinimalFixture_TitleIsNull()
    {
        // fodt-minimal-roundtrip.fodt has no office:meta dc:title
        var result = Parse("fodt-minimal-roundtrip.fodt");
        Assert.Null(result.Title);
    }

    // -------------------------------------------------------------------------
    // Creator, Subject, InitialCreator — absent in both fixtures → null
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_OpaqueNodesFixture_CreatorIsNull()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Null(result.Creator);
    }

    [Fact]
    public void Parse_OpaqueNodesFixture_SubjectIsNull()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Null(result.Subject);
    }

    [Fact]
    public void Parse_OpaqueNodesFixture_InitialCreatorIsNull()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Null(result.InitialCreator);
    }

    // -------------------------------------------------------------------------
    // MimeType and OdfVersion
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_OpaqueNodesFixture_MimeTypeIsCorrect()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Equal("application/vnd.oasis.opendocument.text-flat-xml", result.MimeType);
    }

    [Fact]
    public void Parse_OpaqueNodesFixture_OdfVersionIsCorrect()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.Equal("1.3", result.OdfVersion);
    }

    // -------------------------------------------------------------------------
    // FileSizeBytes
    // -------------------------------------------------------------------------

    [Fact]
    public void Parse_FileSizeBytesIsPositive()
    {
        var result = Parse("fodt-opaque-nodes.fodt");
        Assert.True(result.FileSizeBytes > 0,
            $"Expected FileSizeBytes > 0, got {result.FileSizeBytes}");
    }

    [Fact]
    public void Parse_FileSizeBytesMatchesActualFileSize()
    {
        var path = FixturePath("fodt-opaque-nodes.fodt");
        var actualSize = new FileInfo(path).Length;
        var parser = new FodtParser();
        var result = parser.Parse(path);
        Assert.Equal(actualSize, result.FileSizeBytes);
    }

    // -------------------------------------------------------------------------
    // Dogfood: multi-property consistency across two fixtures
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultiProperty_BothFixturesConsistent()
    {
        var resultOpaque = Parse("fodt-opaque-nodes.fodt");
        var resultMinimal = Parse("fodt-minimal-roundtrip.fodt");

        // Both are successful parses
        Assert.True(resultOpaque.IsSuccess);
        Assert.True(resultMinimal.IsSuccess);

        // opaque-nodes has a title; minimal does not
        Assert.NotNull(resultOpaque.Title);
        Assert.Null(resultMinimal.Title);

        // Both have correct MimeType
        const string expectedMime = "application/vnd.oasis.opendocument.text-flat-xml";
        Assert.Equal(expectedMime, resultOpaque.MimeType);
        Assert.Equal(expectedMime, resultMinimal.MimeType);

        // Both have positive FileSizeBytes
        Assert.True(resultOpaque.FileSizeBytes > 0);
        Assert.True(resultMinimal.FileSizeBytes > 0);

        // ParagraphCount is non-negative for both
        Assert.True(resultOpaque.ParagraphCount >= 0);
        Assert.True(resultMinimal.ParagraphCount >= 0);
    }
}
