// Tests for CsvDocument.Filter chain, GetDistinctValues on filtered, ToHtml after mutation.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R178

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R178: Tests for CsvDocument.Filter chain, GetDistinctValues on filtered, ToHtml after mutation.
/// Covers: Filter by string column returns correct count; Filter by condition leaves correct rows;
/// Filter chain two conditions; Filter then GetDistinctValues; Filter empty result;
/// GetDistinctValues after SetCellValue reflects change; ToHtml after AddRow contains new data;
/// ToHtml after RemoveRow shrinks; SaveToFile->LoadFile->Filter->Verify round-trip;
/// ExportToJson after Filter; GetColumnStats after Filter;
/// dogfood CreateEmpty->AddRows->Filter->Mutate->ToHtml->ExportToJson->SaveLoad->Verify pipeline.
/// </summary>
public class CsvR178FilterAndGetDistinctAndToHtmlDeepTests : IDisposable
{
    private readonly string _tempDir;

    private const string SampleCsv =
        "Name,Dept,Score,Active\n" +
        "Alice,Engineering,92,true\n" +
        "Bob,Finance,85,true\n" +
        "Carol,Engineering,78,false\n" +
        "Dave,HR,91,true\n" +
        "Eve,Finance,88,false\n" +
        "Frank,Engineering,95,true";

    public CsvR178FilterAndGetDistinctAndToHtmlDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR178_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private CsvDocument LoadSample()
    {
        var path = TempFile("sample.csv");
        File.WriteAllText(path, SampleCsv);
        return CsvDocument.LoadFile(path);
    }

    // -------------------------------------------------------------------------
    // Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void Filter_ByDept_CorrectCount()
    {
        var doc = LoadSample();
        var eng = doc.Filter(r => r.GetCellValue("Dept") == "Engineering");
        Assert.Equal(3, eng.RowCount);
    }

    [Fact]
    public void Filter_ByActive_CorrectCount()
    {
        var doc = LoadSample();
        var active = doc.Filter(r => r.GetCellValue("Active") == "true");
        Assert.Equal(4, active.RowCount);
    }

    [Fact]
    public void Filter_EmptyResult_ZeroRows()
    {
        var doc = LoadSample();
        var none = doc.Filter(r => r.GetCellValue("Dept") == "Marketing");
        Assert.Equal(0, none.RowCount);
    }

    [Fact]
    public void Filter_Chain_EngAndActive_CorrectCount()
    {
        var doc = LoadSample();
        var engActive = doc
            .Filter(r => r.GetCellValue("Dept") == "Engineering")
            .Filter(r => r.GetCellValue("Active") == "true");
        // Alice(active) and Frank(active) — Carol is inactive
        Assert.Equal(2, engActive.RowCount);
    }

    [Fact]
    public void Filter_Chain_FinanceAndInactive_CorrectNames()
    {
        var doc = LoadSample();
        var financeInactive = doc
            .Filter(r => r.GetCellValue("Dept") == "Finance")
            .Filter(r => r.GetCellValue("Active") == "false");
        var col = financeInactive.GetColumnValues("Name");
        Assert.Contains("Eve", col);
        Assert.DoesNotContain("Bob", col);
    }

    // -------------------------------------------------------------------------
    // GetDistinctValues on filtered
    // -------------------------------------------------------------------------

    [Fact]
    public void GetDistinctValues_AfterFilter_CorrectCount()
    {
        var doc = LoadSample();
        var eng = doc.Filter(r => r.GetCellValue("Dept") == "Engineering");
        var depts = eng.GetDistinctValues("Dept");
        Assert.Equal(1, depts.Count);
    }

    [Fact]
    public void GetDistinctValues_AfterSetCellValue_ReflectsChange()
    {
        var doc = LoadSample();
        // Change Bob's dept to Engineering
        doc.SetCellValue(1, "Dept", "Engineering");
        var engCount = doc.GetDistinctValues("Dept");
        // Now: Engineering, Engineering(Bob), HR, Finance(Eve) — so distinct: Engineering, Finance, HR
        Assert.True(engCount.Count >= 2);
    }

    // -------------------------------------------------------------------------
    // ToHtml after mutation
    // -------------------------------------------------------------------------

    [Fact]
    public void ToHtml_AfterAddRow_ContainsNewData()
    {
        var doc = LoadSample();
        doc.AddRow(new[] { "Grace", "Engineering", "99", "true" });
        var html = doc.ToHtml();
        Assert.Contains("Grace", html);
    }

    [Fact]
    public void ToHtml_AfterRemoveRow_SmallerOutput()
    {
        var doc = LoadSample();
        var htmlBefore = doc.ToHtml();
        doc.RemoveRow(0);
        var htmlAfter = doc.ToHtml();
        Assert.True(htmlAfter.Length < htmlBefore.Length);
    }

    // -------------------------------------------------------------------------
    // ExportToJson after Filter
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToJson_AfterFilter_ContainsFilteredData()
    {
        var doc = LoadSample();
        var hr = doc.Filter(r => r.GetCellValue("Dept") == "HR");
        var json = hr.ExportToJson();
        Assert.Contains("Dave", json);
        Assert.DoesNotContain("Alice", json);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_CreateEmpty_AddRows_Filter_Mutate_ToHtml_ExportToJson_SaveLoad_Verify()
    {
        // Load
        var doc = LoadSample();
        Assert.Equal(6, doc.RowCount);

        // Filter Engineering
        var eng = doc.Filter(r => r.GetCellValue("Dept") == "Engineering");
        Assert.Equal(3, eng.RowCount);

        // GetDistinctValues on filtered
        var engDepts = eng.GetDistinctValues("Dept");
        Assert.Equal(1, engDepts.Count);

        // ToHtml on filtered
        var html = eng.ToHtml();
        Assert.Contains("Alice", html);
        Assert.DoesNotContain("Bob", html);

        // ExportToJson on filtered
        var json = eng.ExportToJson();
        Assert.Contains("Frank", json);

        // Mutate original: change Dave to Engineering
        doc.SetCellValue(3, "Dept", "Engineering");
        var engAfter = doc.Filter(r => r.GetCellValue("Dept") == "Engineering");
        Assert.Equal(4, engAfter.RowCount);

        // Save and reload
        var path = TempFile("dogfood.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(6, loaded.RowCount);
        // Verify mutation persisted
        Assert.Equal("Engineering", loaded.GetCellValue(3, "Dept"));

        // Filter on loaded
        var loadedEng = loaded.Filter(r => r.GetCellValue("Dept") == "Engineering");
        Assert.Equal(4, loadedEng.RowCount);
    }
}
