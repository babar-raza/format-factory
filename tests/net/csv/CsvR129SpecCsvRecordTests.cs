// Tests for FormatFactory.Csv.Spec.CsvRecord canonical spec-shaped model class.
// Sprint: FORMAT-FACTORY-CSV-R129-20260627
// Ledger: R129-GOVERNED-DOTNET-CSV-SPEC-CSV-RECORD-001

using System.Collections.Generic;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R129: Tests for the canonical spec-shaped model class FormatFactory.Csv.Spec.CsvRecord.
/// CsvRecord (spec_qname: csv:record) represents a single RFC 4180 data row.
/// Fields is an IReadOnlyList of string values. FieldCount is a computed property.
/// Covers: SpecQName constant; Fields default empty; FieldCount=0 for default;
/// Fields assignable; FieldCount matches assigned Fields.Count;
/// single-field record; multi-field record; empty string field is valid;
/// dogfood: create record → verify field access and count.
/// RFC 4180 basis: §2 — each record is a sequence of fields.
/// </summary>
public class CsvR129SpecCsvRecordTests
{
    // -------------------------------------------------------------------------
    // SpecQName constant
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvRecord_SpecQName_IsCorrect()
    {
        Assert.Equal("csv:record", Spec.CsvRecord.SpecQName);
    }

    // -------------------------------------------------------------------------
    // Default state
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvRecord_Fields_DefaultIsEmpty()
    {
        var record = new Spec.CsvRecord();
        Assert.Empty(record.Fields);
    }

    [Fact]
    public void CsvRecord_FieldCount_DefaultIsZero()
    {
        var record = new Spec.CsvRecord();
        Assert.Equal(0, record.FieldCount);
    }

    // -------------------------------------------------------------------------
    // Field assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void CsvRecord_Fields_SingleField_IsAssignable()
    {
        var record = new Spec.CsvRecord { Fields = ["Alice"] };
        Assert.Single(record.Fields);
        Assert.Equal("Alice", record.Fields[0]);
    }

    [Fact]
    public void CsvRecord_Fields_MultipleFields_AreAssignable()
    {
        var fields = new List<string> { "Alice", "95", "NYC" };
        var record = new Spec.CsvRecord { Fields = fields };
        Assert.Equal(3, record.Fields.Count);
        Assert.Equal("Alice", record.Fields[0]);
        Assert.Equal("95",    record.Fields[1]);
        Assert.Equal("NYC",   record.Fields[2]);
    }

    [Fact]
    public void CsvRecord_FieldCount_MatchesFieldsCount()
    {
        var record = new Spec.CsvRecord { Fields = ["A", "B", "C", "D"] };
        Assert.Equal(4, record.FieldCount);
    }

    [Fact]
    public void CsvRecord_Fields_EmptyStringFieldIsValid()
    {
        var record = new Spec.CsvRecord { Fields = ["", "value", ""] };
        Assert.Equal(3, record.FieldCount);
        Assert.Equal(string.Empty, record.Fields[0]);
        Assert.Equal("value",      record.Fields[1]);
        Assert.Equal(string.Empty, record.Fields[2]);
    }

    // -------------------------------------------------------------------------
    // Dogfood: create records and verify field access
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_MultipleRecords_FieldAccess()
    {
        var header = new Spec.CsvRecord { Fields = ["Name", "Score", "City"] };
        var rowA   = new Spec.CsvRecord { Fields = ["Alice", "95", "NYC"] };
        var rowB   = new Spec.CsvRecord { Fields = ["Bob",   "80", "London"] };

        Assert.Equal("csv:record", Spec.CsvRecord.SpecQName);
        Assert.Equal(3, header.FieldCount);
        Assert.Equal(3, rowA.FieldCount);
        Assert.Equal("Alice", rowA.Fields[0]);
        Assert.Equal("London", rowB.Fields[2]);
    }
}
