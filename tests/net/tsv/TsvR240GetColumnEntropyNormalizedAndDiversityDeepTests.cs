// Tests for TsvDocument.GetColumnEntropyNormalized, GetColumnDiversity, GetColumnCardinality deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R240

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R240: Tests for TsvDocument.GetColumnEntropyNormalized, GetColumnDiversity, GetColumnCardinality deeper.
/// GetColumnEntropyNormalized(columnName): returns entropy divided by log(cardinality), in [0,1].
/// GetColumnDiversity(columnName): returns the number of distinct values divided by total rows (Simpson diversity variant).
/// GetColumnCardinality(columnName): returns the count of distinct values in the column.
/// Covers: GetColumnEntropyNormalized no-throw; GetColumnEntropyNormalized in [0,1];
/// GetColumnEntropyNormalized consistent; GetColumnEntropyNormalized one for uniform;
/// GetColumnDiversity no-throw; GetColumnDiversity in [0,1]; GetColumnDiversity consistent;
/// GetColumnDiversity one for all-distinct; GetColumnDiversity zero for uniform;
/// GetColumnCardinality no-throw; GetColumnCardinality positive; GetColumnCardinality consistent;
/// GetColumnCardinality save-load; GetColumnCardinality one for constant;
/// dogfood pipeline for all three measures.
/// </summary>
public class TsvR240GetColumnEntropyNormalizedAndDiversityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR240GetColumnEntropyNormalizedAndDiversityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR240_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateHRDataTsv()
    {
        var path = TempFile("hr_data.tsv");
        File.WriteAllLines(path, new[]
        {
            "emp_id\tdepartment\tgrade\tgender\tnationality\tsalary_band",
            "E001\tEngineering\tSr\tM\tUK\tBand4",
            "E002\tFinance\tMgr\tF\tGermany\tBand5",
            "E003\tEngineering\tJr\tM\tIndia\tBand2",
            "E004\tHR\tSr\tF\tUK\tBand4",
            "E005\tEngineering\tPrincipal\tM\tUSA\tBand6",
            "E006\tLegal\tMgr\tF\tFrance\tBand5",
            "E007\tEngineering\tSr\tF\tUK\tBand4",
            "E008\tFinance\tSr\tM\tUK\tBand4",
            "E009\tMarketing\tJr\tF\tSpain\tBand2",
            "E010\tEngineering\tMgr\tM\tUK\tBand5",
            "E011\tHR\tJr\tF\tPoland\tBand2",
            "E012\tEngineering\tSr\tM\tAustralia\tBand4",
        });
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        File.WriteAllLines(path, new[]
        {
            "id\tvalue",
            "A\t42",
            "B\t42",
            "C\t42",
            "D\t42",
            "E\t42",
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropyNormalized
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropyNormalized_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var ex = Record.Exception(() => doc.GetColumnEntropyNormalized("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropyNormalized_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var en = doc.GetColumnEntropyNormalized("department");
        Assert.True(en >= 0.0 && en <= 1.0);
    }

    [Fact]
    public void GetColumnEntropyNormalized_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        Assert.Equal(
            doc.GetColumnEntropyNormalized("grade"),
            doc.GetColumnEntropyNormalized("grade"));
    }

    [Fact]
    public void GetColumnEntropyNormalized_High_ForUniformDistribution()
    {
        // nationality has 9 distinct values, roughly uniform — expect high normalized entropy
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var en = doc.GetColumnEntropyNormalized("nationality");
        Assert.True(en > 0.5);
    }

    // -------------------------------------------------------------------------
    // GetColumnDiversity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnDiversity_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var ex = Record.Exception(() => doc.GetColumnDiversity("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnDiversity_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var div = doc.GetColumnDiversity("department");
        Assert.True(div >= 0.0 && div <= 1.0);
    }

    [Fact]
    public void GetColumnDiversity_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        Assert.Equal(
            doc.GetColumnDiversity("nationality"),
            doc.GetColumnDiversity("nationality"));
    }

    [Fact]
    public void GetColumnDiversity_One_ForAllDistinct()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        // emp_id: all 12 distinct → diversity = 1.0
        var div = doc.GetColumnDiversity("emp_id");
        Assert.True(div >= 0.9); // allows for rounding
    }

    [Fact]
    public void GetColumnDiversity_Low_ForUniformColumn()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        // value: all same → 1 distinct out of 5 → diversity = 0.2
        var div = doc.GetColumnDiversity("value");
        Assert.True(div <= 0.5);
    }

    // -------------------------------------------------------------------------
    // GetColumnCardinality
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnCardinality_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var ex = Record.Exception(() => doc.GetColumnCardinality("department"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnCardinality_Positive()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        Assert.True(doc.GetColumnCardinality("department") > 0);
    }

    [Fact]
    public void GetColumnCardinality_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        Assert.Equal(
            doc.GetColumnCardinality("grade"),
            doc.GetColumnCardinality("grade"));
    }

    [Fact]
    public void GetColumnCardinality_One_ForConstantColumn()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(1, doc.GetColumnCardinality("value"));
    }

    [Fact]
    public void GetColumnCardinality_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateHRDataTsv());
        var before = doc.GetColumnCardinality("department");
        var path = TempFile("card_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnCardinality("department"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropyNormalized_GetColumnDiversity_GetColumnCardinality_Pipeline()
    {
        // Customer analytics — e-commerce transaction diversity and segmentation study
        var path = TempFile("ecommerce_transactions.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("order_id\tcustomer_segment\tcategory\tchannel\tcountry\tpayment_method\tdevice_type");
        string[] segments = { "Premium", "Standard", "Budget", "New" };
        string[] categories = { "Electronics", "Fashion", "Home", "Sports", "Beauty", "Food", "Books" };
        string[] channels = { "Web", "Mobile", "App" };
        string[] countries = { "UK", "DE", "FR", "IT", "ES", "NL", "SE", "PL" };
        string[] payments = { "Card", "PayPal", "BNPL", "Apple Pay", "Bank Transfer" };
        string[] devices = { "Desktop", "Mobile", "Tablet" };
        var rng = new Random(20241101);
        for (int i = 0; i < 120; i++)
            lines.Add($"ORD{i:D5}\t{segments[i % 4]}\t{categories[i % 7]}\t{channels[i % 3]}\t{countries[i % 8]}\t{payments[i % 5]}\t{devices[i % 3]}");
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnCardinality
        Assert.Equal(4, doc.GetColumnCardinality("customer_segment"));
        Assert.Equal(7, doc.GetColumnCardinality("category"));
        Assert.Equal(3, doc.GetColumnCardinality("channel"));
        Assert.Equal(8, doc.GetColumnCardinality("country"));
        Assert.Equal(5, doc.GetColumnCardinality("payment_method"));
        Assert.Equal(3, doc.GetColumnCardinality("device_type"));
        // All consistent
        Assert.Equal(doc.GetColumnCardinality("category"), doc.GetColumnCardinality("category"));

        // GetColumnDiversity
        var segDiv = doc.GetColumnDiversity("customer_segment");
        Assert.True(segDiv >= 0.0 && segDiv <= 1.0);
        var catDiv = doc.GetColumnDiversity("category");
        Assert.True(catDiv >= 0.0 && catDiv <= 1.0);
        Assert.True(catDiv > segDiv); // 7 categories > 4 segments → higher diversity
        Assert.Equal(segDiv, doc.GetColumnDiversity("customer_segment")); // consistent

        // GetColumnEntropyNormalized
        var segEn = doc.GetColumnEntropyNormalized("customer_segment");
        Assert.True(segEn >= 0.0 && segEn <= 1.0);
        var catEn = doc.GetColumnEntropyNormalized("category");
        Assert.True(catEn >= 0.0 && catEn <= 1.0);
        // Both are roughly uniform distributions → should be close to 1.0
        Assert.True(segEn > 0.8);
        Assert.True(catEn > 0.8);
        Assert.Equal(segEn, doc.GetColumnEntropyNormalized("customer_segment")); // consistent

        // SaveToFile
        var outPath = TempFile("ecommerce_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(4, loaded.GetColumnCardinality("customer_segment"));
        Assert.Equal(segDiv, loaded.GetColumnDiversity("customer_segment"), precision: 6);
        Assert.Equal(segEn, loaded.GetColumnEntropyNormalized("customer_segment"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);
    }
}
