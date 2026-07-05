// Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R306

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R306: Tests for FodtDocument.GetTableCount, AddTable, GetTableRowCount deeper.
/// GetTableCount(): returns the number of tables in the document.
/// AddTable(rows, cols, data): adds a table with the given rows, columns, and cell data.
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
public class FodtR306GetTableCountAndAddTableDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR306GetTableCountAndAddTableDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR306_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Biomedical Engineering: Wearable Sensor Technologies", 1);
        doc.AppendParagraph("Wearable biosensors enable continuous physiological monitoring outside clinical settings.");
        doc.AppendParagraph("Photoplethysmography (PPG) sensors provide non-invasive heart rate and SpO2 measurements.");
        doc.InsertHeading(3, "Sensor Modalities", 2);
        doc.AppendParagraph("Electrodermal activity (EDA) sensors measure sympathetic nervous system arousal via skin conductance.");
        doc.AppendParagraph("Inertial measurement units (IMU) capture motion, posture, and activity classification data.");
        return doc;
    }

    private static string[][] CreatePerformanceTable() => new[]
    {
        new[] { "Metric", "PPG", "EDA", "IMU", "ECG" },
        new[] { "Accuracy", "97.2%", "94.8%", "98.1%", "99.4%" },
        new[] { "Latency (ms)", "45", "120", "15", "8" },
        new[] { "Battery Life (h)", "72", "48", "96", "24" }
    };

    // -------------------------------------------------------------------------
    // GetTableCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetTableCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableCount_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetTableCount() >= 0);
    }

    [Fact]
    public void GetTableCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("No tables in this document.");
        Assert.Equal(0, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_AfterAddTable_Increases()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTableCount();
        doc.AddTable(3, 3, new[]
        {
            new[] { "A", "B", "C" },
            new[] { "1", "2", "3" },
            new[] { "X", "Y", "Z" }
        });
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void GetTableCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddTable(2, 2, new[]
        {
            new[] { "Key", "Value" },
            new[] { "Alpha", "Beta" }
        });
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
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.AddTable(2, 3, new[]
        {
            new[] { "Col1", "Col2", "Col3" },
            new[] { "Val1", "Val2", "Val3" }
        }));
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Increases_Count()
    {
        var doc = CreateRichDoc();
        var before = doc.GetTableCount();
        doc.AddTable(3, 2, new[]
        {
            new[] { "Name", "Score" },
            new[] { "Alice", "92" },
            new[] { "Bob", "88" }
        });
        Assert.Equal(before + 1, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_SaveLoad_Persists()
    {
        var doc = CreateRichDoc();
        doc.AddTable(4, 4, CreatePerformanceTable());
        var before = doc.GetTableCount();
        var path = TempFile("at_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTableCount());
    }

    [Fact]
    public void AddTable_Multiple()
    {
        var doc = CreateRichDoc();
        doc.AddTable(2, 2, new[] { new[] { "A", "B" }, new[] { "1", "2" } });
        doc.AddTable(3, 2, new[] { new[] { "X", "Y" }, new[] { "3", "4" }, new[] { "5", "6" } });
        doc.AddTable(2, 3, new[] { new[] { "P", "Q", "R" }, new[] { "7", "8", "9" } });
        Assert.Equal(3, doc.GetTableCount());
    }

    [Fact]
    public void AddTable_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddTable(3, 3, new[]
        {
            new[] { "H1", "H2", "H3" },
            new[] { "R1C1", "R1C2", "R1C3" },
            new[] { "R2C1", "R2C2", "R2C3" }
        });
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddTable(2, 2, new[]
        {
            new[] { "Feature", "Status" },
            new[] { "Monitoring", "Active" }
        });
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddTable_Then_GetCharCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddTable(2, 2, new[]
        {
            new[] { "Item", "Count" },
            new[] { "Sensors", "4" }
        });
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetTableRowCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTableRowCount_NoThrow()
    {
        var doc = CreateRichDoc();
        doc.AddTable(3, 2, new[]
        {
            new[] { "A", "B" },
            new[] { "1", "2" },
            new[] { "X", "Y" }
        });
        var ex = Record.Exception(() => doc.GetTableRowCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTableRowCount_Positive()
    {
        var doc = CreateRichDoc();
        doc.AddTable(4, 3, CreatePerformanceTable());
        Assert.True(doc.GetTableRowCount(0) > 0);
    }

    [Fact]
    public void GetTableRowCount_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddTable(3, 3, new[]
        {
            new[] { "X", "Y", "Z" },
            new[] { "1", "2", "3" },
            new[] { "A", "B", "C" }
        });
        Assert.Equal(doc.GetTableRowCount(0), doc.GetTableRowCount(0));
    }

    [Fact]
    public void GetTableRowCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        doc.AddTable(4, 4, CreatePerformanceTable());
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
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Renewable Energy Transition: Technology and Policy Analysis", 1);
        doc.AppendParagraph("The global energy transition requires coordinated deployment of renewable technologies across power, heat, and transport.");
        doc.AppendParagraph("Solar photovoltaic costs declined 89% between 2010 and 2023, making utility-scale solar the cheapest electricity source in history.");

        doc.InsertHeading(3, "Technology Performance Benchmarks", 2);
        doc.AppendParagraph("Capacity factors vary significantly across renewable technologies and geographic locations.");

        // Table 1: Technology benchmarks
        doc.AddTable(6, 4, new[]
        {
            new[] { "Technology", "Capacity Factor (%)", "LCOE ($/MWh)", "Lifetime (years)" },
            new[] { "Offshore Wind", "45-55", "80-130", "25" },
            new[] { "Onshore Wind", "25-40", "30-60", "25" },
            new[] { "Utility Solar PV", "15-25", "25-50", "30" },
            new[] { "Pumped Hydro", "30-50", "130-200", "40" },
            new[] { "Grid Battery (4h)", "N/A", "200-350", "15" }
        });
        Assert.Equal(1, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(0) > 0);

        doc.InsertHeading(6, "Policy Mechanisms", 2);
        doc.AppendParagraph("Carbon pricing instruments internalise external costs of fossil fuel combustion into market decisions.");

        // Table 2: Policy effectiveness
        doc.AddTable(5, 3, new[]
        {
            new[] { "Policy Instrument", "Adoption Rate", "Effectiveness Rating" },
            new[] { "Carbon Tax", "High", "★★★★☆" },
            new[] { "Feed-in Tariff", "Very High", "★★★★★" },
            new[] { "Renewable Portfolio Standard", "High", "★★★☆☆" },
            new[] { "Net Metering", "Medium", "★★★☆☆" }
        });
        Assert.Equal(2, doc.GetTableCount());
        Assert.True(doc.GetTableRowCount(1) > 0);

        doc.InsertHeading(doc.GetParagraphCount(), "Investment Flows", 1);
        doc.AppendParagraph("Clean energy investment reached $1.8 trillion in 2023, surpassing fossil fuel investment for the first time.");

        // Table 3: Regional investment breakdown
        doc.AddTable(6, 4, new[]
        {
            new[] { "Region", "Solar ($bn)", "Wind ($bn)", "Storage ($bn)" },
            new[] { "China", "180", "120", "45" },
            new[] { "Europe", "85", "95", "28" },
            new[] { "North America", "75", "65", "38" },
            new[] { "Emerging Markets", "55", "40", "15" },
            new[] { "Rest of World", "35", "25", "8" }
        });
        Assert.Equal(3, doc.GetTableCount());

        // Consistent table counts
        Assert.Equal(doc.GetTableCount(), doc.GetTableCount());

        // GetTableRowCount for all three tables
        var rc0 = doc.GetTableRowCount(0);
        var rc1 = doc.GetTableRowCount(1);
        var rc2 = doc.GetTableRowCount(2);
        Assert.True(rc0 > 0);
        Assert.True(rc1 > 0);
        Assert.True(rc2 > 0);
        Assert.Equal(rc0, doc.GetTableRowCount(0)); // consistent

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
        var path = TempFile("dogfood_energy.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(3, loaded.GetTableCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.Equal(rc0, loaded.GetTableRowCount(0));
        Assert.Equal(rc1, loaded.GetTableRowCount(1));
        Assert.Equal(rc2, loaded.GetTableRowCount(2));

        // AddTable on loaded
        loaded.AddTable(3, 2, new[]
        {
            new[] { "Milestone", "Year" },
            new[] { "1 TW Solar Installed", "2022" },
            new[] { "2 TW Solar Installed", "2025" }
        });
        Assert.Equal(4, loaded.GetTableCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: the renewable energy transition is accelerating beyond initial projections across all key metrics.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_energy_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(4, loaded2.GetTableCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.True(loaded2.GetTableRowCount(0) > 0);
        Assert.True(loaded2.GetTableRowCount(3) > 0);
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddTable(2, 2, new[] { new[] { "X", "Y" }, new[] { "1", "2" } }));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
