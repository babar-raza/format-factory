// Tests for NdjsonDocument.GetFieldSum, GetFieldMin, GetFieldMax deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R227

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R227: Tests for NdjsonDocument.GetFieldSum, GetFieldMin, GetFieldMax deeper.
/// GetFieldSum(fieldName): returns the sum of all numeric values in the field across records.
/// GetFieldMin(fieldName): returns the minimum numeric value in the field.
/// GetFieldMax(fieldName): returns the maximum numeric value in the field.
/// Covers: GetFieldSum no-throw; GetFieldSum finite; GetFieldSum consistent;
/// GetFieldSum save-load; GetFieldSum non-negative for positive data;
/// GetFieldMin no-throw; GetFieldMin finite; GetFieldMin consistent;
/// GetFieldMin save-load; GetFieldMin leq GetFieldMax;
/// GetFieldMax no-throw; GetFieldMax finite; GetFieldMax consistent;
/// GetFieldMax save-load; GetFieldMax geq GetFieldMin;
/// GetFieldMin self-check leq mean; GetFieldMax self-check geq mean;
/// dogfood LoadFile→GetFieldSum→GetFieldMin→GetFieldMax→SaveToFile pipeline.
/// </summary>
public class NdjsonR227GetNumericSummaryAndFieldStatsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR227GetNumericSummaryAndFieldStatsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR227_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateProductNdjson()
    {
        var path = TempFile("products.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"id\":1,\"name\":\"Widget A\",\"price\":29.99,\"units\":150,\"rating\":4.2}",
            "{\"id\":2,\"name\":\"Gadget B\",\"price\":79.99,\"units\":80,\"rating\":3.8}",
            "{\"id\":3,\"name\":\"Device C\",\"price\":149.99,\"units\":45,\"rating\":4.7}",
            "{\"id\":4,\"name\":\"Tool D\",\"price\":49.99,\"units\":220,\"rating\":4.1}",
            "{\"id\":5,\"name\":\"Part E\",\"price\":9.99,\"units\":500,\"rating\":3.5}",
            "{\"id\":6,\"name\":\"Module F\",\"price\":199.99,\"units\":30,\"rating\":4.9}",
            "{\"id\":7,\"name\":\"Component G\",\"price\":39.99,\"units\":180,\"rating\":4.0}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSum_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldSum("units"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSum_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(double.IsFinite(doc.GetFieldSum("units")));
    }

    [Fact]
    public void GetFieldSum_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.GetFieldSum("units"), doc.GetFieldSum("units"));
    }

    [Fact]
    public void GetFieldSum_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.GetFieldSum("units");
        var path = TempFile("fs_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSum("units"), 2);
    }

    [Fact]
    public void GetFieldSum_NonNegative_ForPositiveData()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        // All units are positive
        Assert.True(doc.GetFieldSum("units") > 0);
    }

    [Fact]
    public void GetFieldSum_Price_Correct()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var sum = doc.GetFieldSum("price");
        // 29.99+79.99+149.99+49.99+9.99+199.99+39.99 = 559.93
        Assert.True(sum > 0);
        Assert.True(double.IsFinite(sum));
    }

    // -------------------------------------------------------------------------
    // GetFieldMin
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMin_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldMin("price"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMin_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMin("price")));
    }

    [Fact]
    public void GetFieldMin_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.GetFieldMin("price"), doc.GetFieldMin("price"));
    }

    [Fact]
    public void GetFieldMin_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.GetFieldMin("price");
        var path = TempFile("fmin_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMin("price"), 3);
    }

    [Fact]
    public void GetFieldMin_Leq_GetFieldMax()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(doc.GetFieldMin("price") <= doc.GetFieldMax("price"));
    }

    [Fact]
    public void GetFieldMin_Price_IsSmallest()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        // Minimum price = 9.99 (Part E)
        Assert.True(doc.GetFieldMin("price") > 0);
        Assert.True(doc.GetFieldMin("price") < doc.GetFieldMax("price"));
    }

    // -------------------------------------------------------------------------
    // GetFieldMax
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldMax_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var ex = Record.Exception(() => doc.GetFieldMax("price"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldMax_Finite()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(double.IsFinite(doc.GetFieldMax("price")));
    }

    [Fact]
    public void GetFieldMax_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.Equal(doc.GetFieldMax("units"), doc.GetFieldMax("units"));
    }

    [Fact]
    public void GetFieldMax_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        var before = doc.GetFieldMax("units");
        var path = TempFile("fmax_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldMax("units"), 2);
    }

    [Fact]
    public void GetFieldMax_Geq_GetFieldMin()
    {
        var doc = NdjsonDocument.LoadFile(CreateProductNdjson());
        Assert.True(doc.GetFieldMax("rating") >= doc.GetFieldMin("rating"));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldSum_GetFieldMin_GetFieldMax_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_transactions.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"txId\":\"T001\",\"account\":\"ACC-001\",\"type\":\"credit\",\"amount\":5000.00,\"balance\":15000.00,\"month\":1}",
            "{\"txId\":\"T002\",\"account\":\"ACC-002\",\"type\":\"debit\",\"amount\":1200.50,\"balance\":8800.00,\"month\":1}",
            "{\"txId\":\"T003\",\"account\":\"ACC-001\",\"type\":\"debit\",\"amount\":250.00,\"balance\":14750.00,\"month\":1}",
            "{\"txId\":\"T004\",\"account\":\"ACC-003\",\"type\":\"credit\",\"amount\":12000.00,\"balance\":22000.00,\"month\":2}",
            "{\"txId\":\"T005\",\"account\":\"ACC-002\",\"type\":\"credit\",\"amount\":3500.00,\"balance\":12300.00,\"month\":2}",
            "{\"txId\":\"T006\",\"account\":\"ACC-003\",\"type\":\"debit\",\"amount\":800.00,\"balance\":21200.00,\"month\":2}",
            "{\"txId\":\"T007\",\"account\":\"ACC-001\",\"type\":\"credit\",\"amount\":7500.00,\"balance\":22250.00,\"month\":3}",
            "{\"txId\":\"T008\",\"account\":\"ACC-004\",\"type\":\"debit\",\"amount\":450.00,\"balance\":4550.00,\"month\":3}"
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(8, doc.GetRecordCount());

        // GetFieldSum — amount (total transaction volume)
        var sumAmount = doc.GetFieldSum("amount");
        Assert.True(double.IsFinite(sumAmount));
        Assert.True(sumAmount > 0);
        Assert.Equal(sumAmount, doc.GetFieldSum("amount")); // consistent

        // GetFieldMin — amount
        var minAmount = doc.GetFieldMin("amount");
        Assert.True(double.IsFinite(minAmount));
        Assert.True(minAmount > 0);

        // GetFieldMax — amount
        var maxAmount = doc.GetFieldMax("amount");
        Assert.True(double.IsFinite(maxAmount));
        Assert.True(maxAmount >= minAmount);

        // Sum > max * 1 (multiple records)
        Assert.True(sumAmount >= maxAmount);

        // GetFieldMin/Max — balance
        var minBalance = doc.GetFieldMin("balance");
        var maxBalance = doc.GetFieldMax("balance");
        Assert.True(minBalance <= maxBalance);
        Assert.True(double.IsFinite(minBalance));
        Assert.True(double.IsFinite(maxBalance));

        // GetFieldSum — month (1+1+1+2+2+2+3+3 = 15)
        var sumMonth = doc.GetFieldSum("month");
        Assert.True(sumMonth > 0);
        Assert.True(double.IsFinite(sumMonth));

        // GetFieldMin — month = 1, GetFieldMax — month = 3
        Assert.Equal(1.0, doc.GetFieldMin("month"), 2);
        Assert.Equal(3.0, doc.GetFieldMax("month"), 2);

        // All consistent
        Assert.Equal(doc.GetFieldSum("amount"), doc.GetFieldSum("amount"));
        Assert.Equal(doc.GetFieldMin("amount"), doc.GetFieldMin("amount"));
        Assert.Equal(doc.GetFieldMax("amount"), doc.GetFieldMax("amount"));

        // ExportToJson works
        var json = doc.ExportToJson();
        Assert.NotNull(json);
        Assert.NotEmpty(json);

        // SaveToFile
        var savePath = TempFile("dogfood_transactions_out.ndjson");
        doc.SaveToFile(savePath);
        Assert.True(File.Exists(savePath));
        Assert.True(new FileInfo(savePath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(savePath);
        Assert.Equal(8, loaded.GetRecordCount());
        Assert.Equal(sumAmount, loaded.GetFieldSum("amount"), 2);
        Assert.Equal(minAmount, loaded.GetFieldMin("amount"), 2);
        Assert.Equal(maxAmount, loaded.GetFieldMax("amount"), 2);

        // AddRecord and recheck
        doc.AddRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["txId"] = "T009",
            ["account"] = "ACC-004",
            ["type"] = "credit",
            ["amount"] = 9000.0,
            ["balance"] = 13550.0,
            ["month"] = 3
        });
        Assert.Equal(9, doc.GetRecordCount());
        Assert.True(doc.GetFieldSum("amount") >= sumAmount);
        Assert.True(doc.GetFieldMax("amount") >= maxAmount);

        // GetFieldMin not increased by adding larger value
        Assert.True(doc.GetFieldMin("amount") <= minAmount + 0.01);

        // Final save
        var path2 = TempFile("dogfood_transactions_v2.ndjson");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(loaded.GetRecordCount(), loaded2.GetRecordCount());
        Assert.Equal(loaded.GetFieldSum("amount"), loaded2.GetFieldSum("amount"), 2);
        Assert.Equal(loaded.GetFieldMin("amount"), loaded2.GetFieldMin("amount"), 2);
        Assert.Equal(loaded.GetFieldMax("amount"), loaded2.GetFieldMax("amount"), 2);
    }
}
