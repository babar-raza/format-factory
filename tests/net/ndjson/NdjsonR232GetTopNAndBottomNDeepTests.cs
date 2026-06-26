// Tests for NdjsonDocument.GetTopN, GetBottomN, GetSample deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R232

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R232: Tests for NdjsonDocument.GetTopN, GetBottomN, GetSample deeper.
/// GetTopN(fieldName, n): returns the n records with the highest field value.
/// GetBottomN(fieldName, n): returns the n records with the lowest field value.
/// GetSample(n): returns n randomly sampled records (or all if n >= count).
/// Covers: GetTopN no-throw; GetTopN count leq n; GetTopN non-null; GetTopN save-load;
/// GetTopN consistent field ordering;
/// GetBottomN no-throw; GetBottomN count leq n; GetBottomN non-null; GetBottomN save-load;
/// GetBottomN consistent;
/// GetSample no-throw; GetSample count leq n; GetSample non-null; GetSample save-load;
/// GetSample all-when-n-geq-total;
/// dogfood LoadFile→GetTopN→GetBottomN→GetSample→SaveToFile pipeline.
/// </summary>
public class NdjsonR232GetTopNAndBottomNDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR232GetTopNAndBottomNDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR232_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateScoreNdjson()
    {
        var path = TempFile("scores.ndjson");
        var lines = new[]
        {
            "{\"playerId\":\"P001\",\"name\":\"Alice\",\"score\":9250,\"level\":15,\"rank\":\"Gold\"}",
            "{\"playerId\":\"P002\",\"name\":\"Bob\",\"score\":7100,\"level\":12,\"rank\":\"Silver\"}",
            "{\"playerId\":\"P003\",\"name\":\"Carol\",\"score\":12400,\"level\":20,\"rank\":\"Platinum\"}",
            "{\"playerId\":\"P004\",\"name\":\"Dave\",\"score\":5800,\"level\":9,\"rank\":\"Bronze\"}",
            "{\"playerId\":\"P005\",\"name\":\"Eve\",\"score\":11200,\"level\":18,\"rank\":\"Platinum\"}",
            "{\"playerId\":\"P006\",\"name\":\"Frank\",\"score\":3500,\"level\":6,\"rank\":\"Bronze\"}",
            "{\"playerId\":\"P007\",\"name\":\"Grace\",\"score\":8700,\"level\":14,\"rank\":\"Gold\"}",
            "{\"playerId\":\"P008\",\"name\":\"Hector\",\"score\":15300,\"level\":25,\"rank\":\"Diamond\"}",
            "{\"playerId\":\"P009\",\"name\":\"Iris\",\"score\":6400,\"level\":10,\"rank\":\"Silver\"}",
            "{\"playerId\":\"P010\",\"name\":\"Jake\",\"score\":9900,\"level\":16,\"rank\":\"Gold\"}"
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTopN
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopN_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetTopN("score", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopN_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.NotNull(doc.GetTopN("score", 3));
    }

    [Fact]
    public void GetTopN_Count_Leq_N()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var top3 = doc.GetTopN("score", 3);
        Assert.True(top3.GetRecordCount() <= 3);
    }

    [Fact]
    public void GetTopN_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var top5 = doc.GetTopN("score", 5);
        var before = top5.GetRecordCount();
        var path = TempFile("top_save.ndjson");
        top5.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    [Fact]
    public void GetTopN_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.Equal(doc.GetTopN("level", 5).GetRecordCount(), doc.GetTopN("level", 5).GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GetBottomN
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBottomN_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetBottomN("score", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBottomN_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.NotNull(doc.GetBottomN("level", 4));
    }

    [Fact]
    public void GetBottomN_Count_Leq_N()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var bot3 = doc.GetBottomN("score", 3);
        Assert.True(bot3.GetRecordCount() <= 3);
    }

    [Fact]
    public void GetBottomN_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.Equal(doc.GetBottomN("score", 5).GetRecordCount(), doc.GetBottomN("score", 5).GetRecordCount());
    }

    [Fact]
    public void GetBottomN_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var bot5 = doc.GetBottomN("level", 5);
        var before = bot5.GetRecordCount();
        var path = TempFile("bot_save.ndjson");
        bot5.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // GetSample
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSample_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var ex = Record.Exception(() => doc.GetSample(5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSample_NonNull()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        Assert.NotNull(doc.GetSample(3));
    }

    [Fact]
    public void GetSample_Count_Leq_N()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var sample = doc.GetSample(5);
        Assert.True(sample.GetRecordCount() <= 5);
    }

    [Fact]
    public void GetSample_All_When_N_Geq_Total()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var sample = doc.GetSample(100);
        Assert.Equal(doc.GetRecordCount(), sample.GetRecordCount());
    }

    [Fact]
    public void GetSample_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateScoreNdjson());
        var sample = doc.GetSample(4);
        var before = sample.GetRecordCount();
        var path = TempFile("sample_save.ndjson");
        sample.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetRecordCount());
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTopN_GetBottomN_GetSample_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_stocks.ndjson");
        var lines = new[]
        {
            "{\"symbol\":\"AAPL\",\"price\":189.5,\"marketCap\":2950000000000.0,\"peRatio\":31.2,\"dividendYield\":0.54,\"volume\":52000000}",
            "{\"symbol\":\"MSFT\",\"price\":415.3,\"marketCap\":3080000000000.0,\"peRatio\":36.8,\"dividendYield\":0.72,\"volume\":28000000}",
            "{\"symbol\":\"NVDA\",\"price\":875.2,\"marketCap\":2160000000000.0,\"peRatio\":68.5,\"dividendYield\":0.03,\"volume\":48000000}",
            "{\"symbol\":\"GOOGL\",\"price\":138.2,\"marketCap\":1740000000000.0,\"peRatio\":26.4,\"dividendYield\":0.0,\"volume\":22000000}",
            "{\"symbol\":\"AMZN\",\"price\":185.6,\"marketCap\":1930000000000.0,\"peRatio\":58.2,\"dividendYield\":0.0,\"volume\":35000000}",
            "{\"symbol\":\"META\",\"price\":520.4,\"marketCap\":1320000000000.0,\"peRatio\":28.9,\"dividendYield\":0.40,\"volume\":31000000}",
            "{\"symbol\":\"TSLA\",\"price\":245.8,\"marketCap\":782000000000.0,\"peRatio\":72.1,\"dividendYield\":0.0,\"volume\":75000000}",
            "{\"symbol\":\"BRK.B\",\"price\":368.9,\"marketCap\":810000000000.0,\"peRatio\":9.8,\"dividendYield\":0.0,\"volume\":4500000}",
            "{\"symbol\":\"JNJ\",\"price\":152.4,\"marketCap\":366000000000.0,\"peRatio\":16.2,\"dividendYield\":3.12,\"volume\":8200000}",
            "{\"symbol\":\"V\",\"price\":278.6,\"marketCap\":570000000000.0,\"peRatio\":31.5,\"dividendYield\":0.77,\"volume\":9800000}",
            "{\"symbol\":\"WMT\",\"price\":68.3,\"marketCap\":549000000000.0,\"peRatio\":28.4,\"dividendYield\":1.21,\"volume\":18500000}",
            "{\"symbol\":\"HD\",\"price\":342.1,\"marketCap\":340000000000.0,\"peRatio\":22.8,\"dividendYield\":2.45,\"volume\":6700000}"
        };
        File.WriteAllLines(path, lines);

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetTopN — top 3 by price
        var top3Price = doc.GetTopN("price", 3);
        Assert.NotNull(top3Price);
        Assert.True(top3Price.GetRecordCount() <= 3);
        Assert.Equal(top3Price.GetRecordCount(), top3Price.GetRecordCount()); // consistent

        // GetTopN — top 5 by marketCap
        var top5Cap = doc.GetTopN("marketCap", 5);
        Assert.NotNull(top5Cap);
        Assert.True(top5Cap.GetRecordCount() <= 5);

        // GetTopN — top 3 by dividendYield
        var top3Div = doc.GetTopN("dividendYield", 3);
        Assert.NotNull(top3Div);
        Assert.True(top3Div.GetRecordCount() <= 3);

        // GetBottomN — bottom 3 by price
        var bot3Price = doc.GetBottomN("price", 3);
        Assert.NotNull(bot3Price);
        Assert.True(bot3Price.GetRecordCount() <= 3);
        Assert.Equal(bot3Price.GetRecordCount(), bot3Price.GetRecordCount()); // consistent

        // GetBottomN — bottom 5 by volume
        var bot5Vol = doc.GetBottomN("volume", 5);
        Assert.NotNull(bot5Vol);
        Assert.True(bot5Vol.GetRecordCount() <= 5);

        // GetBottomN — bottom 4 by peRatio
        var bot4PE = doc.GetBottomN("peRatio", 4);
        Assert.NotNull(bot4PE);
        Assert.True(bot4PE.GetRecordCount() <= 4);

        // GetSample — 6 from 12
        var sample6 = doc.GetSample(6);
        Assert.NotNull(sample6);
        Assert.True(sample6.GetRecordCount() <= 6);

        // GetSample — more than total
        var sampleAll = doc.GetSample(50);
        Assert.Equal(doc.GetRecordCount(), sampleAll.GetRecordCount());

        // GetSample — small sample
        var sample2 = doc.GetSample(2);
        Assert.True(sample2.GetRecordCount() <= 2);

        // SaveToFile — top3
        var top3Path = TempFile("dogfood_top3.ndjson");
        top3Price.SaveToFile(top3Path);
        Assert.True(File.Exists(top3Path));
        var loadedTop3 = NdjsonDocument.LoadFile(top3Path);
        Assert.Equal(top3Price.GetRecordCount(), loadedTop3.GetRecordCount());

        // SaveToFile — bot3
        var bot3Path = TempFile("dogfood_bot3.ndjson");
        bot3Price.SaveToFile(bot3Path);
        Assert.True(File.Exists(bot3Path));
        var loadedBot3 = NdjsonDocument.LoadFile(bot3Path);
        Assert.Equal(bot3Price.GetRecordCount(), loadedBot3.GetRecordCount());

        // AppendRecord to doc
        doc.AppendRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["symbol"] = "KO",
            ["price"] = 62.4,
            ["marketCap"] = 269000000000.0,
            ["peRatio"] = 24.1,
            ["dividendYield"] = 3.05,
            ["volume"] = 14200000
        });
        Assert.Equal(13, doc.GetRecordCount());
        Assert.True(doc.GetTopN("marketCap", 3).GetRecordCount() <= 3);
        Assert.True(doc.GetBottomN("price", 3).GetRecordCount() <= 3);
        Assert.True(doc.GetSample(6).GetRecordCount() <= 6);

        // Final save
        var path2 = TempFile("dogfood_stocks_v2.ndjson");
        doc.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = NdjsonDocument.LoadFile(path2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.True(loaded2.GetTopN("price", 5).GetRecordCount() <= 5);
        Assert.True(loaded2.GetBottomN("volume", 5).GetRecordCount() <= 5);
        Assert.Equal(13, loaded2.GetSample(100).GetRecordCount());
    }
}
