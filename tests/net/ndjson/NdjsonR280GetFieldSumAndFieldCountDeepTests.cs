// Tests for NdjsonDocument.GetFieldSum, GetFieldCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R280

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R280: Tests for NdjsonDocument.GetFieldSum, GetFieldCount deeper.
/// GetFieldSum(field): returns the sum of all numeric values in the named field.
/// GetFieldCount(field): returns the count of records with a non-null value in the named field.
/// Covers: GetFieldSum no-throw; GetFieldSum exact for known values; GetFieldSum zero for zero-values;
/// GetFieldSum consistent; GetFieldSum save-load;
/// GetFieldCount no-throw; GetFieldCount positive; GetFieldCount equals RecordCount for fully-populated;
/// GetFieldCount consistent; GetFieldCount save-load;
/// GetFieldSum equals GetFieldMean times GetFieldCount; dogfood pipeline.
/// </summary>
public class NdjsonR280GetFieldSumAndFieldCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR280GetFieldSumAndFieldCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR280_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateSampleNdjson()
    {
        var path = TempFile("sample.ndjson");
        var lines = new StringBuilder();
        // 10 records: amounts 10,20,...,100 → sum=550, count=10
        for (int i = 1; i <= 10; i++)
            lines.AppendLine($"{{\"id\":{i},\"amount\":{i * 10.0},\"label\":\"L{i}\"}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreateZeroNdjson()
    {
        var path = TempFile("zero.ndjson");
        var lines = new StringBuilder();
        for (int i = 0; i < 5; i++)
            lines.AppendLine($"{{\"id\":{i},\"value\":0.0}}");
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    private string CreatePartialNdjson()
    {
        var path = TempFile("partial.ndjson");
        var lines = new StringBuilder();
        // 10 records, only 7 have "score"
        for (int i = 0; i < 7; i++)
            lines.AppendLine($"{{\"id\":{i},\"score\":{i * 3.0}}}");
        for (int i = 7; i < 10; i++)
            lines.AppendLine($"{{\"id\":{i}}}"); // no score field
        File.WriteAllText(path, lines.ToString());
        return path;
    }

    // -------------------------------------------------------------------------
    // GetFieldSum
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldSum_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldSum("amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldSum_Exact_ForKnownValues()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        // 10+20+...+100 = 550
        Assert.Equal(550.0, doc.GetFieldSum("amount"), precision: 6);
    }

    [Fact]
    public void GetFieldSum_Zero_ForZeroValues()
    {
        var doc = NdjsonDocument.LoadFile(CreateZeroNdjson());
        Assert.Equal(0.0, doc.GetFieldSum("value"), precision: 6);
    }

    [Fact]
    public void GetFieldSum_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldSum("amount"), doc.GetFieldSum("amount"));
    }

    [Fact]
    public void GetFieldSum_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldSum("amount");
        var path = TempFile("sum_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldSum("amount"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // GetFieldCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetFieldCount_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var ex = Record.Exception(() => doc.GetFieldCount("amount"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetFieldCount_Positive()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.True(doc.GetFieldCount("amount") > 0);
    }

    [Fact]
    public void GetFieldCount_Equals_RecordCount_ForFullyPopulated()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.RecordCount, doc.GetFieldCount("amount"));
    }

    [Fact]
    public void GetFieldCount_Less_For_PartialField()
    {
        var doc = NdjsonDocument.LoadFile(CreatePartialNdjson());
        Assert.Equal(7, doc.GetFieldCount("score"));
    }

    [Fact]
    public void GetFieldCount_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        Assert.Equal(doc.GetFieldCount("amount"), doc.GetFieldCount("amount"));
    }

    [Fact]
    public void GetFieldCount_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var before = doc.GetFieldCount("amount");
        var path = TempFile("cnt_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetFieldCount("amount"));
    }

    [Fact]
    public void GetFieldSum_Equals_Mean_Times_Count()
    {
        var doc = NdjsonDocument.LoadFile(CreateSampleNdjson());
        var sum = doc.GetFieldSum("amount");
        var mean = doc.GetFieldMean("amount");
        var count = doc.GetFieldCount("amount");
        Assert.Equal(mean * count, sum, precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetFieldSum_GetFieldCount_Pipeline()
    {
        // Transport — TfL / DfT: Contactless Payment Journey Records 2024
        // Aggregated fare revenue and journey count data from London contactless ticketing
        // Field sum and count drive total revenue and average fare calculations

        var path = TempFile("tfl_contactless_journeys_2024.ndjson");
        var sb = new StringBuilder();
        var rng = new Random(20241001);

        string[] lines = {
            "Elizabeth_Line", "Jubilee_Line", "Northern_Line", "Central_Line",
            "Victoria_Line", "Piccadilly_Line", "District_Line", "Circle_Line",
            "Metropolitan_Line", "Bakerloo_Line", "Hammersmith_City", "Overground",
            "DLR", "Elizabeth_Line", "Jubilee_Line"  // Elizabeth and Jubilee appear more
        };
        string[] paymentTypes = { "Contactless_Card", "Contactless_Card", "Apple_Pay", "Google_Pay", "Contactless_Card" };
        string[] ageGroups = { "Adult", "Adult", "Adult", "Adult", "Senior", "Student" };

        for (int i = 0; i < 600; i++)
        {
            string line = lines[rng.Next(lines.Length)];
            string payment = paymentTypes[rng.Next(paymentTypes.Length)];
            string age = ageGroups[rng.Next(ageGroups.Length)];

            // Fare: peaks at Elizabeth Line, standard elsewhere
            bool elizabethLine = line == "Elizabeth_Line";
            double fare = elizabethLine ? 3.40 + rng.NextDouble() * 5.60
                        : age == "Senior" ? 0.0  // free for 60+ in London
                        : age == "Student" ? 1.20 + rng.NextDouble() * 1.50
                        : 1.80 + rng.NextDouble() * 3.20;

            double distanceKm = 1.5 + rng.NextDouble() * 18;
            int durationMins = 5 + rng.Next(0, 55);

            // 5% of records missing distance (card readers offline)
            string distField = rng.NextDouble() < 0.05
                ? "\"distance_km\":null"
                : $"\"distance_km\":{distanceKm:F2}";

            // Free seniors: fare_charged = 0 but still recorded
            sb.AppendLine($"{{\"journey_id\":\"TFL{i:D6}\",\"line\":\"{line}\"," +
                          $"\"payment_type\":\"{payment}\",\"age_group\":\"{age}\"," +
                          $"\"fare_gbp\":{fare:F2},{distField}," +
                          $"\"duration_mins\":{durationMins}}}");
        }
        File.WriteAllText(path, sb.ToString());

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(600, doc.RecordCount);

        // Fare sum and count
        var fareSum = doc.GetFieldSum("fare_gbp");
        var fareCount = doc.GetFieldCount("fare_gbp");
        Assert.True(fareSum >= 0.0);
        Assert.Equal(600, fareCount); // all records have fare (even 0 for seniors)
        Assert.Equal(doc.RecordCount, fareCount);
        Assert.Equal(fareSum, doc.GetFieldSum("fare_gbp")); // consistent
        Assert.Equal(fareCount, doc.GetFieldCount("fare_gbp")); // consistent

        // Sum = mean × count
        var fareMean = doc.GetFieldMean("fare_gbp");
        Assert.Equal(fareMean * fareCount, fareSum, precision: 3);

        // Duration sum and count
        var durSum = doc.GetFieldSum("duration_mins");
        var durCount = doc.GetFieldCount("duration_mins");
        Assert.True(durSum >= 0.0);
        Assert.Equal(600, durCount);

        // Distance: ~5% missing → count < 600
        var distCount = doc.GetFieldCount("distance_km");
        Assert.True(distCount > 0 && distCount <= 600);
        var distSum = doc.GetFieldSum("distance_km");
        Assert.True(distSum >= 0.0);

        // Distance sum = mean × count
        if (distCount > 0)
        {
            var distMean = doc.GetFieldMean("distance_km");
            Assert.Equal(distMean * distCount, distSum, precision: 2);
        }

        // SaveToFile
        var outPath = TempFile("tfl_contactless_out.ndjson");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));
        Assert.True(new FileInfo(outPath).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(outPath);
        Assert.Equal(doc.RecordCount, loaded.RecordCount);
        Assert.Equal(fareSum, loaded.GetFieldSum("fare_gbp"), precision: 6);
        Assert.Equal(fareCount, loaded.GetFieldCount("fare_gbp"));
        Assert.Equal(durSum, loaded.GetFieldSum("duration_mins"), precision: 6);
        Assert.Equal(distCount, loaded.GetFieldCount("distance_km"));

        var ex1 = Record.Exception(() => loaded.GetFieldSum("fare_gbp"));
        var ex2 = Record.Exception(() => loaded.GetFieldCount("distance_km"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
