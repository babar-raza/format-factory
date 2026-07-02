// Type3 (ODF-semantic) tests for FodsDocument.GetResolvedCellStyle / GetResolvedColumnStyle / GetResolvedRowStyle.
// Governance: GI-FODS-NET-001-HEAL TC-GI001-006
// These tests load real .fods fixture files and assert ODF-grounded property values,
// validating that FodsStyleResolver correctly traverses the ODF style chain.

using System.IO;
using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// GI-FODS-NET-001-HEAL TC-GI001-006 — Type3 ODF-semantic tests.
/// Advances Type3 test count from 0 to ≥ 6.
/// Each test loads a real .fods fixture from the output Fixtures/ directory and
/// asserts a concrete ODF-grounded property value via the new style resolver APIs.
/// </summary>
public class FodsR255GetResolvedStyleDedicatedTests
{
    private static string FixturePath(string name)
        => Path.Combine(AppContext.BaseDirectory, "Fixtures", name);

    // T1: Styled cell (0,0) in fods-cell-styles.fods resolves to non-null style object.
    [Fact]
    public void LoadFromFile_StyledCell_ReturnsNonNull()
    {
        var doc = FodsDocument.Load(FixturePath("fods-cell-styles.fods"));
        var style = doc.GetResolvedCellStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
    }

    // T2: Font name is "DejaVu Sans" as declared in the fixture's ODF style chain.
    [Fact]
    public void LoadFromFile_StyledCell_ReturnsExpectedFontName()
    {
        var doc = FodsDocument.Load(FixturePath("fods-cell-styles.fods"));
        var style = doc.GetResolvedCellStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
        Assert.False(string.IsNullOrEmpty(style!.FontName),
            "FontName must be non-empty for the styled cell.");
        Assert.Equal("DejaVu Sans", style.FontName);
    }

    // T3: Font size is 14pt as declared in the fixture (fo:font-size="14pt").
    [Fact]
    public void LoadFromFile_StyledCell_ReturnsExpectedFontSize()
    {
        var doc = FodsDocument.Load(FixturePath("fods-cell-styles.fods"));
        var style = doc.GetResolvedCellStyle("Sheet1", 0, 0);
        Assert.NotNull(style);
        Assert.InRange(style!.FontSize, 13.9, 14.1);
    }

    // T4: Plain cell (0,1) has no style-name → returns default-valued style (FontName null, FontSize 0).
    [Fact]
    public void LoadFromFile_PlainCell_ReturnsDefaultStyle()
    {
        var doc = FodsDocument.Load(FixturePath("fods-cell-styles.fods"));
        var style = doc.GetResolvedCellStyle("Sheet1", 0, 1);
        // Plain cell has no table:style-name — resolver returns a default FodsOdfCellStyle.
        // StyleName must be null and FontName must be null (no style properties).
        Assert.NotNull(style);
        Assert.Null(style!.StyleName);
        Assert.Null(style.FontName);
    }

    // T5: Column 0 in fods-column-widths.fods has style:column-width="2.5cm" → ~70.87 pts.
    [Fact]
    public void LoadFromFile_ColumnStyle_ReturnsWidth()
    {
        var doc = FodsDocument.Load(FixturePath("fods-column-widths.fods"));
        var colStyle = doc.GetResolvedColumnStyle("Sheet1", 0);
        Assert.NotNull(colStyle);
        // 2.5cm * 28.3465 pt/cm ≈ 70.866 pt; allow ±0.1
        Assert.InRange(colStyle!.Width, 70.7, 71.0);
    }

    // T6: Row 0 in fods-column-widths.fods has style:row-height="0.8cm" → ~22.68 pts.
    [Fact]
    public void LoadFromFile_RowStyle_ReturnsHeight()
    {
        var doc = FodsDocument.Load(FixturePath("fods-column-widths.fods"));
        var rowStyle = doc.GetResolvedRowStyle("Sheet1", 0);
        Assert.NotNull(rowStyle);
        // 0.8cm * 28.3465 pt/cm ≈ 22.677 pt; allow ±0.1
        Assert.InRange(rowStyle!.Height, 22.5, 22.8);
    }
}
