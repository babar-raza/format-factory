// FodsRoundtripMutationTests — Deep roundtrip tests for mutation APIs.
// Each test applies a mutation, serializes via ToFodsXml(), reloads via LoadFromXml(),
// and verifies the mutation persisted through the roundtrip.
// Sprint: depth-quality-improvement
// Purpose: Prove that Set* mutations survive save/reload cycles.

using Xunit;

namespace FormatFactory.Fods.Tests;

/// <summary>
/// Roundtrip mutation tests: mutate → save → reload → assert persisted.
/// These tests catch the chart metadata gap (in-memory only, not round-tripped to XML)
/// and any other mutations that fail to persist.
/// </summary>
public class FodsRoundtripMutationTests
{
    // -----------------------------------------------------------------
    // RT-MUT-01: SetCellValue roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_SetCellValue_PersistsThroughReload()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Hello");
        doc.SetCellValue("Sheet1", 1, 0, "World");
        doc.SetCellValue("Sheet1", 0, 1, "42");

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        Assert.Equal("Hello", reloaded.GetCellValue("Sheet1", 0, 0));
        Assert.Equal("World", reloaded.GetCellValue("Sheet1", 1, 0));
        Assert.Equal("42", reloaded.GetCellValue("Sheet1", 0, 1));
    }

    // -----------------------------------------------------------------
    // RT-MUT-02: AddSheet roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_AddSheet_PersistsThroughReload()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.RemoveSheet("Sheet1");
        doc.AddSheet("Alpha");
        doc.AddSheet("Beta");
        doc.AddSheet("Gamma");

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        var names = reloaded.GetSheetNames();
        Assert.Equal(3, names.Count);
        Assert.Contains("Alpha", names);
        Assert.Contains("Beta", names);
        Assert.Contains("Gamma", names);
    }

    // -----------------------------------------------------------------
    // RT-MUT-03: RemoveSheet roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_RemoveSheet_PersistsThroughReload()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.RemoveSheet("Sheet1");
        doc.AddSheet("Keep");
        doc.AddSheet("Remove");
        doc.RemoveSheet("Remove");

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        var names = reloaded.GetSheetNames();
        Assert.Single(names);
        Assert.Equal("Keep", names[0]);
    }

    // -----------------------------------------------------------------
    // RT-MUT-04: SetCellFormula roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_SetCellFormula_PersistsThroughReload()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "10");
        doc.SetCellValue("Sheet1", 1, 0, "20");
        doc.SetCellFormula("Sheet1", 2, 0, "=SUM(A1:A2)");

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        string? formula = reloaded.GetCellFormula("Sheet1", 2, 0);
        Assert.Equal("=SUM(A1:A2)", formula);
    }

    // -----------------------------------------------------------------
    // RT-MUT-05: SetCellFontColor roundtrip
    // Known limitation: font color is in-memory only, not serialized to XML.
    // This test documents the gap — SetCellFontColor does NOT survive roundtrip.
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_SetCellFontColor_DoesNotPersist_KnownGap()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellFontColor("Sheet1", 0, 0, "#FF0000");

        // Verify in-memory mutation works
        Assert.Equal("#FF0000", doc.GetCellFontColor("Sheet1", 0, 0));

        // Roundtrip loses the font color (known gap — style not serialized to ODF XML)
        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        string? color = reloaded.GetCellFontColor("Sheet1", 0, 0);
        Assert.True(string.IsNullOrEmpty(color),
            "Font color is expected to be lost after roundtrip (known serialization gap)");
    }

    // -----------------------------------------------------------------
    // RT-MUT-06: Multiple mutations on same document roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_MultipleMutations_AllPersist()
    {
        var doc = FodsDocument.CreateEmpty();
        doc.AddSheet("Sheet1");
        doc.AddSheet("Data");
        doc.SetCellValue("Data", 0, 0, "Name");
        doc.SetCellValue("Data", 0, 1, "Score");
        doc.SetCellValue("Data", 1, 0, "Alice");
        doc.SetCellValue("Data", 1, 1, "95");
        doc.SetCellValue("Data", 2, 0, "Bob");
        doc.SetCellValue("Data", 2, 1, "87");

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        Assert.Equal("Name", reloaded.GetCellValue("Data", 0, 0));
        Assert.Equal("Score", reloaded.GetCellValue("Data", 0, 1));
        Assert.Equal("Alice", reloaded.GetCellValue("Data", 1, 0));
        Assert.Equal("95", reloaded.GetCellValue("Data", 1, 1));
        Assert.Equal("Bob", reloaded.GetCellValue("Data", 2, 0));
        Assert.Equal("87", reloaded.GetCellValue("Data", 2, 1));
    }

    // -----------------------------------------------------------------
    // RT-MUT-07: Double roundtrip (save → reload → mutate → save → reload)
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_DoubleRoundtrip_DataPreserved()
    {
        // First roundtrip
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "Original");
        string xml1 = doc.ToFodsXml();
        var reloaded1 = FodsDocument.LoadFromXml(xml1);

        // Second mutation + roundtrip
        reloaded1.SetCellValue("Sheet1", 1, 0, "Added");
        string xml2 = reloaded1.ToFodsXml();
        var reloaded2 = FodsDocument.LoadFromXml(xml2);

        Assert.Equal("Original", reloaded2.GetCellValue("Sheet1", 0, 0));
        Assert.Equal("Added", reloaded2.GetCellValue("Sheet1", 1, 0));
    }

    // -----------------------------------------------------------------
    // RT-MUT-08: Empty cell value after roundtrip
    // -----------------------------------------------------------------
    [Fact]
    public void Roundtrip_EmptyAndNonEmptyCells_Preserved()
    {
        var doc = FodsDocument.CreateNew();
        doc.AddSheet("Sheet1");
        doc.SetCellValue("Sheet1", 0, 0, "HasValue");
        // Row 1 col 0 intentionally left empty

        string xml = doc.ToFodsXml();
        var reloaded = FodsDocument.LoadFromXml(xml);

        Assert.Equal("HasValue", reloaded.GetCellValue("Sheet1", 0, 0));
        // Empty cell should return null or empty string
        string? emptyCell = reloaded.GetCellValue("Sheet1", 1, 0);
        Assert.True(string.IsNullOrEmpty(emptyCell),
            $"Expected null or empty for unset cell, got: '{emptyCell}'");
    }
}
