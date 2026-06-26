// Tests for CsvDocument.HasColumn(name) and GetColumn(string headerName).
// Sprint: FORMAT-FACTORY-CSV-R127-20260627
// Ledger: R127-GOVERNED-DOTNET-CSV-HASCOLUMN-GETCOLUMN-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R127: Tests for CsvDocument.HasColumn(string name) and GetColumn(string headerName).
/// HasColumn(name) returns true iff the named header exists (case-sensitive by default).
/// GetColumn(string headerName) returns a List of string values for that column.
/// GetColumn(string) throws when no headers exist or name not found.
/// Covers: column present, column absent, column by index vs by name parity,
/// out-of-range name, no-header document, multi-column document, dogfood pipeline.
/// RFC 4180 basis: §2 fields optionally enclosed in double-quotes.
/// </summary>
public class CsvR127HasColumnAndGetColumnTests
{
    private static CsvDocument LoadSample() =>
        CsvDocument.Load("Name,Score,City\nAlice,95,NYC\nBob,80,London\nCarol,88,Paris");

    private static CsvDocument LoadNoHeader() =>
        CsvDocument.Load("Alice,95,NYC\nBob,80,London", hasHeaders: false);

    // -------------------------------------------------------------------------
    // HasColumn(name)
    // -------------------------------------------------------------------------

    [Fact]
    public void HasColumn_ExistingName_ReturnsTrue()
    {
        var doc = LoadSample();
        Assert.True(doc.HasColumn("Name"));
    }

    [Fact]
    public void HasColumn_SecondColumn_ReturnsTrue()
    {
        var doc = LoadSample();
        Assert.True(doc.HasColumn("Score"));
    }

    [Fact]
    public void HasColumn_LastColumn_ReturnsTrue()
    {
        var doc = LoadSample();
        Assert.True(doc.HasColumn("City"));
    }

    [Fact]
    public void HasColumn_NonExistentName_ReturnsFalse()
    {
        var doc = LoadSample();
        Assert.False(doc.HasColumn("Country"));
    }

    [Fact]
    public void HasColumn_EmptyString_ReturnsFalse()
    {
        var doc = LoadSample();
        Assert.False(doc.HasColumn(string.Empty));
    }

    [Fact]
    public void HasColumn_WrongCase_ReturnsFalse()
    {
        // Headers are case-sensitive: "name" != "Name"
        var doc = LoadSample();
        Assert.False(doc.HasColumn("name"));
    }

    [Fact]
    public void HasColumn_NoHeaderDocument_ReturnsFalse()
    {
        var doc = LoadNoHeader();
        Assert.False(doc.HasColumn("Name"));
    }

    // -------------------------------------------------------------------------
    // GetColumn(string headerName)
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumn_ByName_ReturnsCorrectValues()
    {
        var doc = LoadSample();
        var names = doc.GetColumn("Name");
        Assert.Equal(3, names.Count);
        Assert.Equal("Alice", names[0]);
        Assert.Equal("Bob", names[1]);
        Assert.Equal("Carol", names[2]);
    }

    [Fact]
    public void GetColumn_ByName_NumericColumn_AllValuesPresent()
    {
        var doc = LoadSample();
        var scores = doc.GetColumn("Score");
        Assert.Contains("95", scores);
        Assert.Contains("80", scores);
        Assert.Contains("88", scores);
    }

    [Fact]
    public void GetColumn_ByName_ParityWithIndexOverload()
    {
        var doc = LoadSample();
        var byName = doc.GetColumn("City");
        var byIndex = doc.GetColumn(2);
        Assert.Equal(byIndex, byName);
    }

    // -------------------------------------------------------------------------
    // Dogfood: HasColumn gate → GetColumn pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_HasColumnGate_ThenGetColumn()
    {
        var doc = CsvDocument.Load(
            "Product,Region,Revenue\nWidget,West,1000\nGadget,East,800\nWidget,East,900");

        // Gate: only extract if column exists
        Assert.True(doc.HasColumn("Product"));
        Assert.True(doc.HasColumn("Revenue"));
        Assert.False(doc.HasColumn("Profit"));

        var products = doc.GetColumn("Product");
        Assert.Equal(3, products.Count);
        Assert.Contains("Widget", products);
        Assert.Contains("Gadget", products);

        var revenues = doc.GetColumn("Revenue");
        Assert.Equal(3, revenues.Count);
        Assert.Contains("1000", revenues);
        Assert.Contains("800", revenues);
    }
}
