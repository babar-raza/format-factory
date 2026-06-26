// Tests for Spec.TsvRecord canonical spec-shaped model class.
// Sprint: FORMAT-FACTORY-TSV-R127-20260627
// Ledger: R127-GOVERNED-DOTNET-TSV-SPEC-TSVRECORD-001

using System;
using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R127: Tests for FormatFactory.Tsv.Spec.TsvRecord — the canonical spec-shaped model
/// class for TSV row records. SpecQName = "tsv:record"; Fields default empty (init-only);
/// FieldCount matches Fields.Count; Fields are assignable via collection expression.
/// Covers: SpecQName constant; Fields default empty; FieldCount zero for empty fields;
/// Fields init-only assignment; FieldCount matches assigned list; single-field record;
/// multi-field record; whitespace preserved in fields; empty string field; null-safe
/// FieldCount access; dogfood TSV parse → TsvRecord composition pipeline.
/// </summary>
public class TsvR127SpecTsvRecordTests
{
    // -------------------------------------------------------------------------
    // SpecQName constant
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvRecord_SpecQName_IsCorrect()
    {
        Assert.Equal("tsv:record", Spec.TsvRecord.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Fields default value
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvRecord_Fields_DefaultIsEmpty()
    {
        var rec = new Spec.TsvRecord();
        Assert.Empty(rec.Fields);
    }

    // -------------------------------------------------------------------------
    // FieldCount derived property
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvRecord_FieldCount_ZeroForDefaultFields()
    {
        var rec = new Spec.TsvRecord();
        Assert.Equal(0, rec.FieldCount);
    }

    [Fact]
    public void TsvRecord_FieldCount_MatchesFieldsCount()
    {
        var rec = new Spec.TsvRecord { Fields = ["Alpha", "Beta", "Gamma", "Delta"] };
        Assert.Equal(4, rec.FieldCount);
    }

    // -------------------------------------------------------------------------
    // Fields init-only assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvRecord_SingleField_AssignableAndAccessible()
    {
        var rec = new Spec.TsvRecord { Fields = ["solo"] };
        Assert.Equal(1, rec.FieldCount);
        Assert.Equal("solo", rec.Fields[0]);
    }

    [Fact]
    public void TsvRecord_MultiField_AllValuesPreserved()
    {
        var fields = new[] { "Name", "Age", "City" };
        var rec = new Spec.TsvRecord { Fields = fields };
        Assert.Equal(3, rec.FieldCount);
        Assert.Equal("Name", rec.Fields[0]);
        Assert.Equal("Age", rec.Fields[1]);
        Assert.Equal("City", rec.Fields[2]);
    }

    [Fact]
    public void TsvRecord_WhitespaceInField_IsPreserved()
    {
        var rec = new Spec.TsvRecord { Fields = ["  leading", "trailing  ", " both "] };
        Assert.Equal("  leading", rec.Fields[0]);
        Assert.Equal("trailing  ", rec.Fields[1]);
        Assert.Equal(" both ", rec.Fields[2]);
    }

    [Fact]
    public void TsvRecord_EmptyStringField_IsPreserved()
    {
        var rec = new Spec.TsvRecord { Fields = ["A", "", "C"] };
        Assert.Equal(3, rec.FieldCount);
        Assert.Equal("", rec.Fields[1]);
    }

    // -------------------------------------------------------------------------
    // SpecQName is class-level constant
    // -------------------------------------------------------------------------

    [Fact]
    public void TsvRecord_SpecQName_AccessibleWithoutInstance()
    {
        // const is accessible without instantiation
        const string expected = "tsv:record";
        Assert.Equal(expected, Spec.TsvRecord.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Dogfood: TsvDocument.Load → row values → TsvRecord composition
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_TsvLoadThenTsvRecordComposition()
    {
        const string content = "Product\tRegion\tRevenue\nWidget\tWest\t1000\nGadget\tEast\t800";
        var doc = TsvDocument.Load(content, hasHeaders: true);

        Assert.Equal(2, doc.RowCount);

        // Compose TsvRecord instances from TsvDocument rows
        var records = new List<Spec.TsvRecord>();
        foreach (var row in doc.Rows)
        {
            records.Add(new Spec.TsvRecord { Fields = row });
        }

        Assert.Equal(2, records.Count);
        Assert.Equal("Widget", records[0].Fields[0]);
        Assert.Equal("West",   records[0].Fields[1]);
        Assert.Equal("1000",   records[0].Fields[2]);
        Assert.Equal("Gadget", records[1].Fields[0]);
        Assert.Equal("East",   records[1].Fields[1]);
        Assert.Equal("800",    records[1].Fields[2]);

        // Verify FieldCount matches column count
        Assert.Equal(doc.ColumnCount, records[0].FieldCount);
    }
}
