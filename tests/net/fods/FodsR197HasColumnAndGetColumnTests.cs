// Tests for FodsDocument.HasColumn and FodsDocument.GetColumn (by header name).
// Sprint: ff-sal-id-fix-20260626-221238
// Ledger: PC-FODS-R197
// Spec: FACT-FODS-006 (table:table-cell), FACT-FODS-003 (table:table-row)
// ODF §9.4.5: table:table-cell — R197 column lookup by header name.

using Xunit;
using FormatFactory.Fods;

namespace FormatFactory.Fods.Tests;

public sealed class FodsR197HasColumnAndGetColumnTests
{
    // ── helpers ──────────────────────────────────────────────────────────────

    private static FodsDocument MakeSheet()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Data");
        // Row 0: headers
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 0, 2, "Grade");
        // Row 1
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "92");
        doc.SetCellValue("Data", 1, 2, "A");
        // Row 2
        doc.SetCellValue("Data", 2, 0, "Bob");
        doc.SetCellValue("Data", 2, 1, "78");
        doc.SetCellValue("Data", 2, 2, "B");
        return doc;
    }

    // ── HasColumn ─────────────────────────────────────────────────────────────

    [Fact]
    public void HasColumn_ExistingHeader_ReturnsTrue()
    {
        var doc = MakeSheet();
        Assert.True(doc.HasColumn("Data", "Name"));
        Assert.True(doc.HasColumn("Data", "Score"));
        Assert.True(doc.HasColumn("Data", "Grade"));
    }

    [Fact]
    public void HasColumn_MissingHeader_ReturnsFalse()
    {
        var doc = MakeSheet();
        Assert.False(doc.HasColumn("Data", "Email"));
    }

    [Fact]
    public void HasColumn_CaseSensitive_ReturnsFalse()
    {
        var doc = MakeSheet();
        Assert.False(doc.HasColumn("Data", "name")); // lower-case, should not match "Name"
    }

    [Fact]
    public void HasColumn_NullOrWhitespaceSheetName_Throws()
    {
        var doc = MakeSheet();
        Assert.Throws<ArgumentException>(() => doc.HasColumn("", "Name"));
        Assert.Throws<ArgumentException>(() => doc.HasColumn("   ", "Name"));
    }

    [Fact]
    public void HasColumn_NullHeader_Throws()
    {
        var doc = MakeSheet();
        Assert.Throws<ArgumentNullException>(() => doc.HasColumn("Data", null!));
    }

    // ── GetColumn ─────────────────────────────────────────────────────────────

    [Fact]
    public void GetColumn_ExistingHeader_ReturnsDataRows()
    {
        var doc = MakeSheet();
        var names = doc.GetColumn("Data", "Name");
        Assert.Equal(2, names.Count);
        Assert.Equal("Alice", names[0]);
        Assert.Equal("Bob", names[1]);
    }

    [Fact]
    public void GetColumn_ScoreColumn_ReturnsNumericStrings()
    {
        var doc = MakeSheet();
        var scores = doc.GetColumn("Data", "Score");
        Assert.Equal(2, scores.Count);
        Assert.Equal("92", scores[0]);
        Assert.Equal("78", scores[1]);
    }

    [Fact]
    public void GetColumn_MissingHeader_Throws()
    {
        var doc = MakeSheet();
        Assert.Throws<InvalidOperationException>(() => doc.GetColumn("Data", "Email"));
    }

    [Fact]
    public void GetColumn_NonexistentSheet_Throws()
    {
        var doc = MakeSheet();
        Assert.Throws<InvalidOperationException>(() => doc.GetColumn("Missing", "Name"));
    }

    [Fact]
    public void GetColumn_HeaderRowExcluded_CountEqualsDataRows()
    {
        var doc = MakeSheet();
        // 3 total rows (row 0 = header, rows 1-2 = data) => GetColumn returns 2 items
        var col = doc.GetColumn("Data", "Grade");
        Assert.Equal(2, col.Count);
        Assert.DoesNotContain("Grade", col); // header value must not appear in result
    }

    [Fact]
    public void GetColumn_ReturnsIReadOnlyList()
    {
        var doc = MakeSheet();
        var result = doc.GetColumn("Data", "Name");
        Assert.IsAssignableFrom<IReadOnlyList<string?>>(result);
    }

    [Fact]
    public void HasColumn_ThenGetColumn_Dogfood()
    {
        // Dogfood: guard with HasColumn, then GetColumn
        var doc = MakeSheet();
        const string header = "Score";
        Assert.True(doc.HasColumn("Data", header));
        var values = doc.GetColumn("Data", header);
        Assert.Equal(2, values.Count);
        Assert.All(values, v => Assert.False(string.IsNullOrEmpty(v)));
    }
}
