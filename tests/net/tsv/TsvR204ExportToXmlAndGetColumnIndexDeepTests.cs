// Tests for TsvDocument.ExportToXml, GetColumnIndex, MergeWith deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R204

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R204: Tests for TsvDocument.ExportToXml, GetColumnIndex, MergeWith deeper.
/// ExportToXml(): exports the document as an XML string.
/// GetColumnIndex(colName): returns the zero-based index of the named column.
/// MergeWith(other): returns a new document combining rows from both documents.
/// Covers: ExportToXml non-null; ExportToXml non-empty; ExportToXml has root;
/// ExportToXml has header names; ExportToXml has data; ExportToXml after AddRow grows;
/// ExportToXml after Filter shrinks; ExportToXml consistent; ExportToXml save-load;
/// GetColumnIndex=0 for Name; GetColumnIndex=1 for Team; GetColumnIndex=2 for Score;
/// GetColumnIndex negative for unknown; GetColumnIndex consistent; GetColumnIndex no-throw;
/// GetColumnIndex after AddColumn; GetColumnIndex after RemoveColumn;
/// MergeWith non-null; MergeWith sum row count; MergeWith all rows present;
/// MergeWith preserves headers; MergeWith no-throw; MergeWith persist;
/// MergeWith then Filter; MergeWith then SortRows; MergeWith self doubles;
/// MergeWith then ExportToXml grows; MergeWith then GetColumnIndex consistent;
/// dogfood LoadFile→ExportToXml→GetColumnIndex→MergeWith→SaveToFile pipeline.
/// </summary>
public class TsvR204ExportToXmlAndGetColumnIndexDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR204ExportToXmlAndGetColumnIndexDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR204_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleTsv()
    {
        var path = TempFile("sample.tsv");
        var content =
            "Name\tTeam\tScore\tCity\n" +
            "Alice\tAlpha\t92\tLondon\n" +
            "Bob\tBeta\t78\tParis\n" +
            "Carol\tAlpha\t88\tBerlin\n" +
            "Dave\tGamma\t85\tRome\n" +
            "Eve\tAlpha\t95\tMadrid\n";
        File.WriteAllText(path, content);
        return path;
    }

    private string CreateSecondTsv()
    {
        var path = TempFile("second.tsv");
        var content =
            "Name\tTeam\tScore\tCity\n" +
            "Frank\tDelta\t80\tOslo\n" +
            "Grace\tBeta\t91\tVienna\n" +
            "Hank\tGamma\t74\tWarsaw\n";
        File.WriteAllText(path, content);
        return path;
    }

    // -------------------------------------------------------------------------
    // ExportToXml
    // -------------------------------------------------------------------------

    [Fact]
    public void ExportToXml_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotNull(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_NonEmpty()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.NotEmpty(doc.ExportToXml());
    }

    [Fact]
    public void ExportToXml_HasRoot()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("<") && xml.Contains(">"));
    }

    [Fact]
    public void ExportToXml_HasHeaderNames()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Name") || xml.Contains("Team") || xml.Contains("Score"));
    }

    [Fact]
    public void ExportToXml_HasData()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var xml = doc.ExportToXml();
        Assert.True(xml.Contains("Alice") || xml.Contains("Bob") || xml.Contains("Carol"));
    }

    [Fact]
    public void ExportToXml_AfterAddRow_Grows()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToXml().Length;
        doc.AddRow(new[] { "Frank", "Delta", "80", "Oslo" });
        Assert.True(doc.ExportToXml().Length > before);
    }

    [Fact]
    public void ExportToXml_AfterFilter_Shrinks()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.ExportToXml().Length;
        var filtered = doc.Filter("Team", "Gamma");
        Assert.True(filtered.ExportToXml().Length < before);
    }

    [Fact]
    public void ExportToXml_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.ExportToXml().Length, doc.ExportToXml().Length);
    }

    [Fact]
    public void ExportToXml_SaveLoad()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var path = TempFile("xml_saveload.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        var xml = loaded.ExportToXml();
        Assert.NotNull(xml);
        Assert.NotEmpty(xml);
    }

    // -------------------------------------------------------------------------
    // GetColumnIndex
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnIndex_Name_Is0()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(0, doc.GetColumnIndex("Name"));
    }

    [Fact]
    public void GetColumnIndex_Team_Is1()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(1, doc.GetColumnIndex("Team"));
    }

    [Fact]
    public void GetColumnIndex_Score_Is2()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(2, doc.GetColumnIndex("Score"));
    }

    [Fact]
    public void GetColumnIndex_City_Is3()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(3, doc.GetColumnIndex("City"));
    }

    [Fact]
    public void GetColumnIndex_Negative_ForUnknown()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.True(doc.GetColumnIndex("NonExistentCol_XYZ") < 0);
    }

    [Fact]
    public void GetColumnIndex_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        Assert.Equal(doc.GetColumnIndex("Name"), doc.GetColumnIndex("Name"));
    }

    [Fact]
    public void GetColumnIndex_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var ex = Record.Exception(() => doc.GetColumnIndex("Name"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnIndex_AfterAddColumn()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.AddColumn("Region", new[] { "EU", "EU", "EU", "EU", "EU" });
        Assert.Equal(4, doc.GetColumnIndex("Region"));
    }

    [Fact]
    public void GetColumnIndex_AfterRemoveColumn()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        doc.RemoveColumn("City");
        Assert.True(doc.GetColumnIndex("City") < 0);
        Assert.Equal(2, doc.GetColumnIndex("Score")); // Score still at 2
    }

    // -------------------------------------------------------------------------
    // MergeWith
    // -------------------------------------------------------------------------

    [Fact]
    public void MergeWith_NonNull()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        Assert.NotNull(doc1.MergeWith(doc2));
    }

    [Fact]
    public void MergeWith_SumRowCount()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(doc1.GetRowCount() + doc2.GetRowCount(), merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_AllRowsPresent()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var merged = doc1.MergeWith(doc2);
        var names = merged.GetColumnValues("Name");
        Assert.Contains("Alice", names);
        Assert.Contains("Frank", names);
        Assert.Contains("Grace", names);
    }

    [Fact]
    public void MergeWith_PreservesHeaders()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(doc1.GetHeaderCount(), merged.GetHeaderCount());
    }

    [Fact]
    public void MergeWith_NoThrow()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var ex = Record.Exception(() => doc1.MergeWith(doc2));
        Assert.Null(ex);
    }

    [Fact]
    public void MergeWith_Persist()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var merged = doc1.MergeWith(doc2);
        var path = TempFile("merged_persist.tsv");
        merged.SaveToFile(path);
        Assert.True(File.Exists(path));
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(8, loaded.GetRowCount());
    }

    [Fact]
    public void MergeWith_ThenFilter()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var merged = doc1.MergeWith(doc2);
        var filtered = merged.Filter("Team", "Beta");
        Assert.Equal(2, filtered.GetRowCount()); // Bob and Grace
    }

    [Fact]
    public void MergeWith_SelfDoubles()
    {
        var doc = TsvDocument.LoadFile(CreateSampleTsv());
        var before = doc.GetRowCount();
        var merged = doc.MergeWith(doc);
        Assert.Equal(before * 2, merged.GetRowCount());
    }

    [Fact]
    public void MergeWith_ThenExportToXml_Grows()
    {
        var doc1 = TsvDocument.LoadFile(CreateSampleTsv());
        var doc2 = TsvDocument.LoadFile(CreateSecondTsv());
        var before = doc1.ExportToXml().Length;
        var merged = doc1.MergeWith(doc2);
        Assert.True(merged.ExportToXml().Length > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_ExportToXml_GetColumnIndex_MergeWith_SaveToFile_Pipeline()
    {
        // Create two TSV sources
        var path1 = TempFile("dogfood_src1.tsv");
        var content1 =
            "Employee\tDepartment\tGrade\tSalary\n" +
            "Alice\tEngineering\tSenior\t95000\n" +
            "Bob\tMarketing\tJunior\t55000\n" +
            "Carol\tEngineering\tLead\t115000\n" +
            "Dave\tFinance\tMid\t72000\n";
        File.WriteAllText(path1, content1);

        var path2 = TempFile("dogfood_src2.tsv");
        var content2 =
            "Employee\tDepartment\tGrade\tSalary\n" +
            "Eve\tEngineering\tSenior\t98000\n" +
            "Frank\tMarketing\tSenior\t82000\n" +
            "Grace\tFinance\tJunior\t48000\n";
        File.WriteAllText(path2, content2);

        var doc1 = TsvDocument.LoadFile(path1);
        var doc2 = TsvDocument.LoadFile(path2);

        Assert.Equal(4, doc1.GetRowCount());
        Assert.Equal(3, doc2.GetRowCount());

        // GetColumnIndex on doc1
        Assert.Equal(0, doc1.GetColumnIndex("Employee"));
        Assert.Equal(1, doc1.GetColumnIndex("Department"));
        Assert.Equal(2, doc1.GetColumnIndex("Grade"));
        Assert.Equal(3, doc1.GetColumnIndex("Salary"));
        Assert.True(doc1.GetColumnIndex("NonExistent") < 0);

        // ExportToXml baseline
        var xml1 = doc1.ExportToXml();
        Assert.NotNull(xml1);
        Assert.NotEmpty(xml1);
        Assert.True(xml1.Contains("<") && xml1.Contains(">"));
        Assert.True(xml1.Contains("Employee") || xml1.Contains("Alice"));

        // MergeWith
        var merged = doc1.MergeWith(doc2);
        Assert.Equal(7, merged.GetRowCount());
        Assert.Equal(4, merged.GetHeaderCount());

        // GetColumnIndex on merged (same headers)
        Assert.Equal(0, merged.GetColumnIndex("Employee"));
        Assert.Equal(3, merged.GetColumnIndex("Salary"));

        // ExportToXml on merged grows
        var xmlMerged = merged.ExportToXml();
        Assert.True(xmlMerged.Length > xml1.Length);

        // All rows present in merged
        var empNames = merged.GetColumnValues("Employee");
        Assert.Contains("Alice", empNames);
        Assert.Contains("Eve", empNames);
        Assert.Contains("Grace", empNames);
        Assert.Equal(7, empNames.Count);

        // Filter merged by Engineering
        var engMerged = merged.Filter("Department", "Engineering");
        Assert.Equal(3, engMerged.GetRowCount()); // Alice, Carol, Eve

        // GetColumnIndex on filtered
        Assert.Equal(0, engMerged.GetColumnIndex("Employee"));

        // ExportToXml on filtered shrinks vs merged
        var xmlEng = engMerged.ExportToXml();
        Assert.True(xmlEng.Length < xmlMerged.Length);

        // SortRows on merged
        merged.SortRows("Salary", ascending: false);
        Assert.Equal(7, merged.GetRowCount());
        Assert.Equal("115000", merged.GetCell(0, 3)); // Carol highest

        // AddColumn to merged
        merged.AddColumn("Level", new[] { "L6", "L2", "L6", "L3", "L5", "L4", "L1" });
        Assert.Equal(5, merged.GetHeaderCount());
        Assert.Equal(4, merged.GetColumnIndex("Level"));

        // ExportToXml grows after AddColumn
        var xmlAfterAdd = merged.ExportToXml();
        Assert.True(xmlAfterAdd.Length > xmlMerged.Length);

        // RemoveColumn
        merged.RemoveColumn("Level");
        Assert.True(merged.GetColumnIndex("Level") < 0);
        Assert.Equal(4, merged.GetHeaderCount());

        // MergeWith merged and doc1 = 11 rows
        var bigMerge = merged.MergeWith(doc1);
        Assert.Equal(11, bigMerge.GetRowCount());

        // ExportToXml consistent
        var x1 = merged.ExportToXml();
        var x2 = merged.ExportToXml();
        Assert.Equal(x1.Length, x2.Length);

        // GetColumnIndex consistent
        Assert.Equal(merged.GetColumnIndex("Employee"), merged.GetColumnIndex("Employee"));

        // SaveToFile merged
        var saveMerged = TempFile("dogfood_merged.tsv");
        merged.SaveToFile(saveMerged);
        Assert.True(File.Exists(saveMerged));

        // LoadFile and verify
        var loadedMerged = TsvDocument.LoadFile(saveMerged);
        Assert.Equal(7, loadedMerged.GetRowCount());
        Assert.Equal(0, loadedMerged.GetColumnIndex("Employee"));

        // ExportToXml on loaded
        var loadedXml = loadedMerged.ExportToXml();
        Assert.NotNull(loadedXml);
        Assert.NotEmpty(loadedXml);

        // MergeWith on loaded
        var loadedMerge2 = loadedMerged.MergeWith(doc2);
        Assert.Equal(10, loadedMerge2.GetRowCount());

        // Final SaveToFile
        var path3 = TempFile("dogfood_merged_v2.tsv");
        loadedMerge2.SaveToFile(path3);
        Assert.True(File.Exists(path3));
        var loaded2 = TsvDocument.LoadFile(path3);
        Assert.Equal(10, loaded2.GetRowCount());
        Assert.Equal(0, loaded2.GetColumnIndex("Employee"));
    }
}
