// Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R319

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R319: Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// AddTable(rows, cols): adds a table with the given dimensions to the document.
/// GetTableRowCount(tableIndex): returns the number of rows in the table at the given index.
/// Covers: GetTableCount no-throw; GetTableCount non-negative; GetTableCount consistent;
/// GetTableCount zero for new doc; GetTableCount after AddTable increases; GetTableCount save-load;
/// AddTable no-throw; AddTable increases count; AddTable save-load;
/// AddTable multiple; AddTable then ExportToHtml no-throw; AddTable then ExportToMarkdown no-throw;
/// AddTable then GetCharCount positive;
/// GetTableRowCount no-throw; GetTableRowCount positive; GetTableRowCount consistent;
/// GetTableRowCount save-load;
/// dogfood CreateDoc→AddTable→GetTableCount→GetTableRowCount→SaveToFile pipeline.
/// </summary>
public class FodtR319GetTableCountAndAddTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR319GetTableCountAndAddTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR319_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateResearchDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Comparative Analysis of Renewable Energy Storage Technologies", 1);
        doc.AppendParagraph("Grid-scale energy storage is the critical enabling technology for transitioning to high-penetration variable renewable energy systems.");
        doc.AppendParagraph("Battery energy storage systems, pumped hydro, and compressed air energy storage represent the three dominant commercial-scale solutions.");
        doc.InsertHeading(3, "Technology Comparison", 2);
        doc.AppendParagraph("Levelised cost of storage (LCOS) comparisons must account for cycle life, round-trip efficiency, and capital cost amortisation periods.");
        doc.AppendParagraph("Lithium-ion batteries demonstrate superior energy density but face supply chain constraints from cobalt and lithium procurement.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateResearchDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateResearchDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with prose but no tables.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAddTable_Increases()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetTableCount();
        doc.AddTable(4, 3);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(5, 4);
        var before = doc.GetTableCount();
        var path = TempFile("tc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    // -------------------------------------------------------------------------
    // AddTable
    // -------------------------------------------------------------------------

    [Fact]
    public void AddTable_NoThrow()
    {
        var doc = CreateResearchDoc();
        var ex = Record.Exception(() => doc.AddTable(3, 3));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Increases_Count()
    {
        var doc = CreateResearchDoc();
        var before = doc.GetTableCount();
        doc.AddTable(6, 4);
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_SaveLoad_Persists()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(4, 5);
        var before = doc.GetTableCount();
        var path = TempFile("at_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void AddTable_Multiple()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(3, 3);
        doc.AddTable(5, 2);
        doc.AddTable(7, 4);
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(4, 3);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(3, 4);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_GetCharCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(4, 3);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NoThrow()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(5, 3);
        var ex = Record.Exception(() => doc.GetTableRowCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableRowCount_Positive()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(6, 4);
        Assert.True(doc.GetTableRowCount(0) > 0);
    }

    [Fact]
    public void GetTableRowCount_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(4, 3);
        Assert.Equal(doc.GetTableRowCount(0), doc.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableRowCount_SaveLoad_Consistent()
    {
        var doc = CreateResearchDoc();
        doc.AddTable(7, 3);
        var before = doc.GetTableRowCount(0);
        var path = TempFile("trc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableRowCount(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddTable_GetTableCount_GetTableRowCount_SaveToFile_Pipeline()
    {
        // Technical feasibility study — hydrogen fuel cell vehicle comparison report
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Hydrogen Fuel Cell Vehicle Technology: Feasibility Assessment and Market Analysis", 1);
        doc.AppendParagraph("Hydrogen fuel cell electric vehicles (FCEVs) offer zero tailpipe emissions with energy densities competitive with conventional internal combustion engines.");
        doc.AppendParagraph("Proton exchange membrane (PEM) fuel cells operate at 60-80°C with high power density, making them suitable for automotive applications requiring rapid start-up.");

        doc.InsertHeading(3, "Powertrain Comparison", 2);
        doc.AppendParagraph("FCEVs achieve 50-60% fuel-to-wheel efficiency compared to 20-25% for conventional ICE vehicles and 77-90% for battery electric vehicles.");
        doc.AppendParagraph("Refuelling time of 3-5 minutes for FCEVs closely mirrors conventional fuel station experience, addressing range anxiety barriers present in BEV adoption.");

        doc.InsertHeading(6, "Infrastructure Requirements", 2);
        doc.AppendParagraph("Hydrogen refuelling infrastructure requires capital expenditure of $1-2 million per station, compared to $50,000-200,000 for DC fast charging equipment.");
        doc.AppendParagraph("Green hydrogen production via electrolysis powered by renewable energy achieves lifecycle emissions below 30g CO2-equivalent per kilometre.");

        doc.InsertHeading(9, "Market Projections", 1);
        doc.AppendParagraph("BloombergNEF projects 6.7 million FCEV units globally by 2040, driven by commercial vehicle adoption in heavy transport and logistics sectors.");
        doc.AppendParagraph("Toyota, Hyundai, and Honda lead passenger FCEV commercialisation while Daimler, Volvo, and Scania target long-haul FCEV trucking by 2027.");

        Assert.Equal(12, doc.GetParagraphCount());

        // GetTableCount — zero initially
        Assert.Equal(0, doc.GetTableCount());

        // AddTable — powertrain comparison (7 rows × 4 cols: metric/ICE/BEV/FCEV)
        doc.AddTable(7, 4);
        Assert.Equal(1, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(0) >= 7);

        // AddTable — hydrogen production pathways (5 rows × 3 cols: method/cost/emissions)
        doc.AddTable(5, 3);
        Assert.Equal(2, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(1) >= 5);

        // AddTable — refuelling infrastructure comparison (6 rows × 4 cols: metric/current/2030/2040)
        doc.AddTable(6, 4);
        Assert.Equal(3, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(2) >= 6);

        // AddTable — OEM FCEV programme timeline (8 rows × 3 cols: manufacturer/model/launch_year)
        doc.AddTable(8, 3);
        Assert.Equal(4, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(3) >= 8);

        // Consistent
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
        Assert.Equal(doc.GetTableRowCount(0), doc.GetTableRowCount(0));

        // ExportToHtml works
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown works
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText works
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount positive
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_hydrogen_fcev.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetTableCount());
        Assert.True(loaded.GetTableRowCount(0) >= 7);
        Assert.True(loaded.GetTableRowCount(1) >= 5);
        Assert.True(loaded.GetTableRowCount(2) >= 6);
        Assert.True(loaded.GetTableRowCount(3) >= 8);
        Assert.True(loaded.GetParagraphCount() > 0);

        // AddTable on loaded
        loaded.AddTable(5, 4);
        Assert.Equal(5, loaded.GetTableCount());
        Assert.True(loaded.GetTableRowCount(4) >= 5);

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: hydrogen fuel cell vehicles represent a viable decarbonisation pathway for long-range, heavy-duty, and commercial transport segments.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_hydrogen_fcev_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.True(loaded2.GetTableRowCount(0) >= 7);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddTable(3, 3));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
