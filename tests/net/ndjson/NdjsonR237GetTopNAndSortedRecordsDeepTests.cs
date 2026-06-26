// Tests for NdjsonDocument.GetTopNByField, GetBottomNByField, GetSortedRecords deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-NDJSON-R237

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

/// <summary>
/// R237: Tests for NdjsonDocument.GetTopNByField, GetBottomNByField, GetSortedRecords deeper.
/// GetTopNByField(field, n): returns the top N records ordered by field descending.
/// GetBottomNByField(field, n): returns the bottom N records ordered by field ascending.
/// GetSortedRecords(field, ascending): returns all records sorted by the given field.
/// Covers: GetTopNByField no-throw; GetTopNByField count leq n; GetTopNByField consistent;
/// GetTopNByField zero for n=0; GetTopNByField save-load;
/// GetBottomNByField no-throw; GetBottomNByField count leq n; GetBottomNByField consistent;
/// GetBottomNByField save-load;
/// GetSortedRecords no-throw; GetSortedRecords count equals record count; GetSortedRecords consistent;
/// GetSortedRecords save-load;
/// dogfood CreateDoc→GetTopNByField→GetBottomNByField→GetSortedRecords→SaveToFile pipeline.
/// </summary>
public class NdjsonR237GetTopNAndSortedRecordsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public NdjsonR237GetTopNAndSortedRecordsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "NdjsonR237_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateLeaderboardNdjson()
    {
        var path = TempFile("leaderboard.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"player_id\":\"P001\",\"username\":\"AlphaWolf\",\"score\":9850,\"level\":42,\"wins\":128,\"losses\":32,\"rank\":\"Diamond\"}",
            "{\"player_id\":\"P002\",\"username\":\"BetaStorm\",\"score\":7420,\"level\":38,\"wins\":95,\"losses\":45,\"rank\":\"Platinum\"}",
            "{\"player_id\":\"P003\",\"username\":\"GammaRay\",\"score\":12300,\"level\":55,\"wins\":185,\"losses\":20,\"rank\":\"Master\"}",
            "{\"player_id\":\"P004\",\"username\":\"DeltaForce\",\"score\":5100,\"level\":28,\"wins\":62,\"losses\":58,\"rank\":\"Gold\"}",
            "{\"player_id\":\"P005\",\"username\":\"EpsilonX\",\"score\":8750,\"level\":40,\"wins\":112,\"losses\":38,\"rank\":\"Diamond\"}",
            "{\"player_id\":\"P006\",\"username\":\"ZetaBlaze\",\"score\":3200,\"level\":18,\"wins\":38,\"losses\":72,\"rank\":\"Silver\"}",
            "{\"player_id\":\"P007\",\"username\":\"EtaPulse\",\"score\":15000,\"level\":65,\"wins\":220,\"losses\":15,\"rank\":\"Grandmaster\"}",
            "{\"player_id\":\"P008\",\"username\":\"ThetaVoid\",\"score\":6300,\"level\":33,\"wins\":78,\"losses\":50,\"rank\":\"Platinum\"}",
            "{\"player_id\":\"P009\",\"username\":\"IotaFlame\",\"score\":11200,\"level\":50,\"wins\":162,\"losses\":28,\"rank\":\"Master\"}",
            "{\"player_id\":\"P010\",\"username\":\"KappaWave\",\"score\":2800,\"level\":14,\"wins\":28,\"losses\":85,\"rank\":\"Bronze\"}"
        });
        return path;
    }

    // -------------------------------------------------------------------------
    // GetTopNByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopNByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var ex = Record.Exception(() => doc.GetTopNByField("score", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopNByField_Count_LeqN()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var top3 = doc.GetTopNByField("score", 3);
        Assert.True(top3.Count <= 3);
    }

    [Fact]
    public void GetTopNByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var t1 = doc.GetTopNByField("score", 5);
        var t2 = doc.GetTopNByField("score", 5);
        Assert.Equal(t1.Count, t2.Count);
    }

    [Fact]
    public void GetTopNByField_Zero_ForNZero()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var top0 = doc.GetTopNByField("score", 0);
        Assert.Equal(0, top0.Count);
    }

    [Fact]
    public void GetTopNByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var before = doc.GetTopNByField("score", 3).Count;
        var path = TempFile("tn_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTopNByField("score", 3).Count);
    }

    // -------------------------------------------------------------------------
    // GetBottomNByField
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBottomNByField_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var ex = Record.Exception(() => doc.GetBottomNByField("score", 3));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBottomNByField_Count_LeqN()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var bot3 = doc.GetBottomNByField("score", 3);
        Assert.True(bot3.Count <= 3);
    }

    [Fact]
    public void GetBottomNByField_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var b1 = doc.GetBottomNByField("wins", 4);
        var b2 = doc.GetBottomNByField("wins", 4);
        Assert.Equal(b1.Count, b2.Count);
    }

    [Fact]
    public void GetBottomNByField_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var before = doc.GetBottomNByField("level", 3).Count;
        var path = TempFile("bn_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBottomNByField("level", 3).Count);
    }

    // -------------------------------------------------------------------------
    // GetSortedRecords
    // -------------------------------------------------------------------------

    [Fact]
    public void GetSortedRecords_NoThrow()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var ex = Record.Exception(() => doc.GetSortedRecords("score", ascending: false));
        Assert.Null(ex);
    }

    [Fact]
    public void GetSortedRecords_Count_EqualsRecordCount()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        Assert.Equal(doc.GetRecordCount(), doc.GetSortedRecords("score", ascending: true).Count);
    }

    [Fact]
    public void GetSortedRecords_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var s1 = doc.GetSortedRecords("level", ascending: false);
        var s2 = doc.GetSortedRecords("level", ascending: false);
        Assert.Equal(s1.Count, s2.Count);
    }

    [Fact]
    public void GetSortedRecords_SaveLoad_Consistent()
    {
        var doc = NdjsonDocument.LoadFile(CreateLeaderboardNdjson());
        var before = doc.GetSortedRecords("score", ascending: false).Count;
        var path = TempFile("sr_save.ndjson");
        doc.SaveToFile(path);
        var loaded = NdjsonDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetSortedRecords("score", ascending: false).Count);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetTopNByField_GetBottomNByField_GetSortedRecords_SaveToFile_Pipeline()
    {
        var path = TempFile("dogfood_mutual_funds.ndjson");
        File.WriteAllLines(path, new[]
        {
            "{\"fund_id\":\"MF001\",\"fund_name\":\"Global Growth\",\"category\":\"Equity\",\"aum_bn\":28.4,\"return_1y\":0.182,\"return_3y\":0.142,\"return_5y\":0.118,\"expense_ratio\":0.0075,\"sharpe_ratio\":1.42,\"max_drawdown\":-0.18}",
            "{\"fund_id\":\"MF002\",\"fund_name\":\"Income Plus\",\"category\":\"Bond\",\"aum_bn\":42.1,\"return_1y\":0.048,\"return_3y\":0.052,\"return_5y\":0.058,\"expense_ratio\":0.0045,\"sharpe_ratio\":0.82,\"max_drawdown\":-0.06}",
            "{\"fund_id\":\"MF003\",\"fund_name\":\"Tech Disruptors\",\"category\":\"Equity\",\"aum_bn\":12.8,\"return_1y\":0.315,\"return_3y\":0.228,\"return_5y\":0.195,\"expense_ratio\":0.0095,\"sharpe_ratio\":1.85,\"max_drawdown\":-0.32}",
            "{\"fund_id\":\"MF004\",\"fund_name\":\"Balanced Core\",\"category\":\"Mixed\",\"aum_bn\":65.2,\"return_1y\":0.092,\"return_3y\":0.088,\"return_5y\":0.082,\"expense_ratio\":0.0055,\"sharpe_ratio\":1.12,\"max_drawdown\":-0.12}",
            "{\"fund_id\":\"MF005\",\"fund_name\":\"Emerging Markets\",\"category\":\"Equity\",\"aum_bn\":18.6,\"return_1y\":0.142,\"return_3y\":0.098,\"return_5y\":0.085,\"expense_ratio\":0.0115,\"sharpe_ratio\":0.95,\"max_drawdown\":-0.28}",
            "{\"fund_id\":\"MF006\",\"fund_name\":\"Corporate Bonds\",\"category\":\"Bond\",\"aum_bn\":35.8,\"return_1y\":0.062,\"return_3y\":0.068,\"return_5y\":0.072,\"expense_ratio\":0.0040,\"sharpe_ratio\":0.98,\"max_drawdown\":-0.08}",
            "{\"fund_id\":\"MF007\",\"fund_name\":\"Small Cap Value\",\"category\":\"Equity\",\"aum_bn\":8.2,\"return_1y\":0.225,\"return_3y\":0.178,\"return_5y\":0.148,\"expense_ratio\":0.0085,\"sharpe_ratio\":1.58,\"max_drawdown\":-0.22}",
            "{\"fund_id\":\"MF008\",\"fund_name\":\"Real Estate\",\"category\":\"REIT\",\"aum_bn\":22.4,\"return_1y\":0.082,\"return_3y\":0.075,\"return_5y\":0.095,\"expense_ratio\":0.0065,\"sharpe_ratio\":0.88,\"max_drawdown\":-0.15}",
            "{\"fund_id\":\"MF009\",\"fund_name\":\"ESG Leaders\",\"category\":\"Equity\",\"aum_bn\":31.5,\"return_1y\":0.158,\"return_3y\":0.132,\"return_5y\":0.112,\"expense_ratio\":0.0080,\"sharpe_ratio\":1.35,\"max_drawdown\":-0.16}",
            "{\"fund_id\":\"MF010\",\"fund_name\":\"Infrastructure\",\"category\":\"Alternative\",\"aum_bn\":14.2,\"return_1y\":0.068,\"return_3y\":0.072,\"return_5y\":0.088,\"expense_ratio\":0.0090,\"sharpe_ratio\":1.05,\"max_drawdown\":-0.10}",
            "{\"fund_id\":\"MF011\",\"fund_name\":\"Dividend Focus\",\"category\":\"Equity\",\"aum_bn\":48.6,\"return_1y\":0.108,\"return_3y\":0.098,\"return_5y\":0.092,\"expense_ratio\":0.0060,\"sharpe_ratio\":1.22,\"max_drawdown\":-0.13}",
            "{\"fund_id\":\"MF012\",\"fund_name\":\"Government Bonds\",\"category\":\"Bond\",\"aum_bn\":82.3,\"return_1y\":0.032,\"return_3y\":0.038,\"return_5y\":0.042,\"expense_ratio\":0.0020,\"sharpe_ratio\":0.65,\"max_drawdown\":-0.04}"
        });

        var doc = NdjsonDocument.LoadFile(path);
        Assert.Equal(12, doc.GetRecordCount());

        // GetTopNByField — top 3 by return_1y
        var top3Return = doc.GetTopNByField("return_1y", 3);
        Assert.NotNull(top3Return);
        Assert.True(top3Return.Count <= 3);
        Assert.True(top3Return.Count > 0);

        // GetTopNByField — top 5 by sharpe_ratio
        var top5Sharpe = doc.GetTopNByField("sharpe_ratio", 5);
        Assert.True(top5Sharpe.Count <= 5);

        // GetTopNByField — top 12 (all records)
        var topAll = doc.GetTopNByField("aum_bn", 12);
        Assert.True(topAll.Count <= 12);

        // GetTopNByField — zero for n=0
        var topZero = doc.GetTopNByField("return_1y", 0);
        Assert.Equal(0, topZero.Count);

        // Consistent
        Assert.Equal(top3Return.Count, doc.GetTopNByField("return_1y", 3).Count);

        // GetBottomNByField — bottom 3 by expense_ratio (cheapest funds)
        var bot3Expense = doc.GetBottomNByField("expense_ratio", 3);
        Assert.NotNull(bot3Expense);
        Assert.True(bot3Expense.Count <= 3);
        Assert.True(bot3Expense.Count > 0);

        // GetBottomNByField — bottom 5 by max_drawdown (most negative = highest risk)
        var bot5Drawdown = doc.GetBottomNByField("max_drawdown", 5);
        Assert.True(bot5Drawdown.Count <= 5);

        // GetSortedRecords — ascending by return_1y
        var sortedAsc = doc.GetSortedRecords("return_1y", ascending: true);
        Assert.Equal(12, sortedAsc.Count);

        // GetSortedRecords — descending by sharpe_ratio
        var sortedDesc = doc.GetSortedRecords("sharpe_ratio", ascending: false);
        Assert.Equal(12, sortedDesc.Count);

        // GetSortedRecords — by aum_bn
        var sortedAum = doc.GetSortedRecords("aum_bn", ascending: false);
        Assert.Equal(12, sortedAum.Count);

        // Consistent sort
        Assert.Equal(sortedAsc.Count, doc.GetSortedRecords("return_1y", ascending: true).Count);

        // SaveToFile
        var out1 = TempFile("dogfood_funds_out.ndjson");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = NdjsonDocument.LoadFile(out1);
        Assert.Equal(12, loaded.GetRecordCount());
        Assert.Equal(top3Return.Count, loaded.GetTopNByField("return_1y", 3).Count);
        Assert.Equal(12, loaded.GetSortedRecords("sharpe_ratio", ascending: false).Count);

        // AddRecord on loaded
        loaded.AddRecord(new System.Collections.Generic.Dictionary<string, object>
        {
            ["fund_id"] = "MF013",
            ["fund_name"] = "Climate Transition",
            ["category"] = "Equity",
            ["aum_bn"] = 5.8,
            ["return_1y"] = 0.195,
            ["return_3y"] = 0.162,
            ["return_5y"] = 0.138,
            ["expense_ratio"] = 0.0090,
            ["sharpe_ratio"] = 1.48,
            ["max_drawdown"] = -0.20
        });
        Assert.Equal(13, loaded.GetRecordCount());
        Assert.Equal(13, loaded.GetSortedRecords("return_1y", ascending: true).Count);

        // Final save
        var out2 = TempFile("dogfood_funds_v2.ndjson");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = NdjsonDocument.LoadFile(out2);
        Assert.Equal(13, loaded2.GetRecordCount());
        Assert.True(loaded2.GetTopNByField("return_1y", 3).Count <= 3);
        Assert.True(loaded2.GetBottomNByField("expense_ratio", 3).Count <= 3);
        Assert.Equal(13, loaded2.GetSortedRecords("aum_bn", ascending: false).Count);
        var ex1 = Record.Exception(() => loaded2.GetTopNByField("sharpe_ratio", 5));
        var ex2 = Record.Exception(() => loaded2.GetBottomNByField("max_drawdown", 3));
        var ex3 = Record.Exception(() => loaded2.GetSortedRecords("return_5y", ascending: true));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
