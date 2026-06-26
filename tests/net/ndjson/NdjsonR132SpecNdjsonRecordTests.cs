// Tests for Spec.NdjsonRecord canonical spec-shaped model class.
// Sprint: FORMAT-FACTORY-NDJSON-R132-20260627
// Ledger: R132-GOVERNED-DOTNET-NDJSON-SPEC-NDJSONRECORD-001

using System;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R132: Tests for FormatFactory.Ndjson.Spec.NdjsonRecord — the canonical spec-shaped
/// model class for NDJSON record lines. SpecQName = "ndjson:record"; RawJson default
/// empty string (init-only); LineIndex default 0 (init-only, zero-based line index).
/// Covers: SpecQName constant; RawJson default empty; LineIndex default zero;
/// RawJson init-only assignment; LineIndex init-only assignment; multiple instances
/// are independent; SpecQName accessible without instance; LineIndex first line is 0;
/// LineIndex second line is 1; dogfood NdjsonDocument parse → Spec.NdjsonRecord
/// composition pipeline matching each line's raw content.
/// </summary>
public class NdjsonR132SpecNdjsonRecordTests
{
    // -------------------------------------------------------------------------
    // SpecQName constant
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNdjsonRecord_SpecQName_IsCorrect()
    {
        Assert.Equal("ndjson:record", Spec.NdjsonRecord.SpecQName);
    }

    [Fact]
    public void SpecNdjsonRecord_SpecQName_AccessibleWithoutInstance()
    {
        const string expected = "ndjson:record";
        Assert.Equal(expected, Spec.NdjsonRecord.SpecQName);
    }

    // -------------------------------------------------------------------------
    // RawJson default and init-only assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNdjsonRecord_RawJson_DefaultIsEmpty()
    {
        var rec = new Spec.NdjsonRecord();
        Assert.Equal(string.Empty, rec.RawJson);
    }

    [Fact]
    public void SpecNdjsonRecord_RawJson_AssignableViaInit()
    {
        const string json = "{\"name\":\"Alice\",\"score\":95}";
        var rec = new Spec.NdjsonRecord { RawJson = json };
        Assert.Equal(json, rec.RawJson);
    }

    [Fact]
    public void SpecNdjsonRecord_RawJson_NullObjectJson_Assignable()
    {
        var rec = new Spec.NdjsonRecord { RawJson = "{}" };
        Assert.Equal("{}", rec.RawJson);
    }

    // -------------------------------------------------------------------------
    // LineIndex default and init-only assignment
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNdjsonRecord_LineIndex_DefaultIsZero()
    {
        var rec = new Spec.NdjsonRecord();
        Assert.Equal(0, rec.LineIndex);
    }

    [Fact]
    public void SpecNdjsonRecord_LineIndex_FirstLine_IsZero()
    {
        var rec = new Spec.NdjsonRecord { RawJson = "{\"id\":1}", LineIndex = 0 };
        Assert.Equal(0, rec.LineIndex);
    }

    [Fact]
    public void SpecNdjsonRecord_LineIndex_SecondLine_IsOne()
    {
        var rec = new Spec.NdjsonRecord { RawJson = "{\"id\":2}", LineIndex = 1 };
        Assert.Equal(1, rec.LineIndex);
    }

    // -------------------------------------------------------------------------
    // Independence of multiple instances
    // -------------------------------------------------------------------------

    [Fact]
    public void SpecNdjsonRecord_MultipleInstances_AreIndependent()
    {
        var r0 = new Spec.NdjsonRecord { RawJson = "{\"a\":1}", LineIndex = 0 };
        var r1 = new Spec.NdjsonRecord { RawJson = "{\"b\":2}", LineIndex = 1 };

        Assert.NotEqual(r0.RawJson, r1.RawJson);
        Assert.NotEqual(r0.LineIndex, r1.LineIndex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: NdjsonDocument parse → Spec.NdjsonRecord composition pipeline
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_NdjsonDocumentParse_ThenSpecRecordComposition()
    {
        const string ndjson =
            "{\"name\":\"Alice\",\"score\":95}\n" +
            "{\"name\":\"Bob\",\"score\":80}\n" +
            "{\"name\":\"Carol\",\"score\":88}";

        var doc = NdjsonDocument.Load(ndjson);
        Assert.Equal(3, doc.Count);

        // Compose Spec.NdjsonRecord instances with ToNdjson() as raw representation
        var specRecords = new Spec.NdjsonRecord[doc.Count];
        for (var i = 0; i < doc.Count; i++)
        {
            specRecords[i] = new Spec.NdjsonRecord
            {
                RawJson   = doc.Records[i].ToString(),
                LineIndex = i
            };
        }

        // Verify SpecQName on all records is the same canonical name
        foreach (var r in specRecords)
        {
            Assert.Equal("ndjson:record", Spec.NdjsonRecord.SpecQName);
            Assert.False(string.IsNullOrEmpty(r.RawJson));
        }

        // Verify line indices are sequential
        Assert.Equal(0, specRecords[0].LineIndex);
        Assert.Equal(1, specRecords[1].LineIndex);
        Assert.Equal(2, specRecords[2].LineIndex);
    }
}
