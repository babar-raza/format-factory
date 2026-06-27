// Tests for CsvDocument.GetColumnMode, GetColumnMedian, GetColumnTrimmedMean deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-CSV-R238

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R238: Tests for CsvDocument.GetColumnMode, GetColumnMedian, GetColumnTrimmedMean deeper.
/// GetColumnMode(col): returns the most frequently occurring value in the column.
/// GetColumnMedian(col): returns the median of a numeric column.
/// GetColumnTrimmedMean(col, trimFraction): returns the mean after trimming extreme values.
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnMode correct for known data; GetColumnMode save-load;
/// GetColumnMedian no-throw; GetColumnMedian in range; GetColumnMedian consistent;
/// GetColumnMedian save-load;
/// GetColumnTrimmedMean no-throw; GetColumnTrimmedMean in range; GetColumnTrimmedMean consistent;
/// GetColumnTrimmedMean save-load;
/// dogfood Append→GetColumnMode→GetColumnMedian→GetColumnTrimmedMean→SaveToFile pipeline.
/// </summary>
public class CsvR238GetColumnModeAndMedianDeepTests : IDisposable
{
    private readonly string _tempDir;

    public CsvR238GetColumnModeAndMedianDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "CsvR238_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateStudentCsv()
    {
        var path = TempFile("students.csv");
        var lines = new[]
        {
            "student_id,subject,grade,score,year,school",
            "S001,Mathematics,A,92,Year12,North",
            "S002,Science,B,75,Year11,South",
            "S003,Mathematics,A,88,Year12,East",
            "S004,English,B,78,Year11,North",
            "S005,Mathematics,C,64,Year10,West",
            "S006,Science,A,91,Year12,South",
            "S007,English,B,72,Year11,East",
            "S008,Mathematics,A,95,Year12,North",
            "S009,Science,C,58,Year10,West",
            "S010,English,B,80,Year12,Central",
            "S011,Mathematics,B,83,Year11,South",
            "S012,Science,A,90,Year12,North"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var ex = Record.Exception(() => doc.GetColumnMode("subject"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        Assert.NotNull(doc.GetColumnMode("subject"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        Assert.Equal(doc.GetColumnMode("grade"), doc.GetColumnMode("grade"));
    }

    [Fact]
    public void GetColumnMode_Correct_ForKnownData()
    {
        // Mathematics appears 5 times — most frequent subject
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        Assert.Equal("Mathematics", doc.GetColumnMode("subject"));
    }

    [Fact]
    public void GetColumnMode_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var before = doc.GetColumnMode("grade");
        var path = TempFile("mode_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMode("grade"));
    }

    // -------------------------------------------------------------------------
    // GetColumnMedian
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMedian_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var ex = Record.Exception(() => doc.GetColumnMedian("score"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMedian_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var median = doc.GetColumnMedian("score");
        Assert.True(median >= doc.GetColumnMin("score"));
        Assert.True(median <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnMedian_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        Assert.Equal(doc.GetColumnMedian("score"), doc.GetColumnMedian("score"), precision: 4);
    }

    [Fact]
    public void GetColumnMedian_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var before = doc.GetColumnMedian("score");
        var path = TempFile("med_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnMedian("score"), precision: 2);
    }

    // -------------------------------------------------------------------------
    // GetColumnTrimmedMean
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnTrimmedMean_NoThrow()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var ex = Record.Exception(() => doc.GetColumnTrimmedMean("score", 0.1));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnTrimmedMean_InRange()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var tm = doc.GetColumnTrimmedMean("score", 0.1);
        Assert.True(tm >= doc.GetColumnMin("score"));
        Assert.True(tm <= doc.GetColumnMax("score"));
    }

    [Fact]
    public void GetColumnTrimmedMean_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        Assert.Equal(doc.GetColumnTrimmedMean("score", 0.2), doc.GetColumnTrimmedMean("score", 0.2), precision: 4);
    }

    [Fact]
    public void GetColumnTrimmedMean_SaveLoad_Consistent()
    {
        var doc = CsvDocument.LoadFile(CreateStudentCsv());
        var before = doc.GetColumnTrimmedMean("score", 0.1);
        var path = TempFile("tm_save.csv");
        doc.SaveToFile(path);
        var loaded = CsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnTrimmedMean("score", 0.1), precision: 2);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnMedian_GetColumnTrimmedMean_SaveToFile_Pipeline()
    {
        // Sports analytics — Premier League player performance dataset
        var path = TempFile("dogfood_pl_players.csv");
        var lines = new[]
        {
            "player_id,name,position,club,goals,assists,minutes_played,rating,nationality",
            "PL001,Player_A,Forward,Arsenal,18,7,2840,7.8,English",
            "PL002,Player_B,Midfielder,Chelsea,5,14,3100,7.5,Spanish",
            "PL003,Player_C,Defender,ManCity,2,3,3200,7.2,Brazilian",
            "PL004,Player_D,Forward,Liverpool,24,9,2650,8.4,Egyptian",
            "PL005,Player_E,Midfielder,ManUtd,8,11,2980,7.4,Norwegian",
            "PL006,Player_F,Forward,Tottenham,15,5,2700,7.7,Korean",
            "PL007,Player_G,Midfielder,Arsenal,6,13,3050,7.6,German",
            "PL008,Player_H,Defender,Chelsea,1,2,3300,7.1,French",
            "PL009,Player_I,Forward,ManCity,20,6,2580,8.1,Norwegian",
            "PL010,Player_J,Midfielder,Liverpool,9,10,2920,7.3,Dutch",
            "PL011,Player_K,Defender,ManUtd,3,4,3150,7.0,English",
            "PL012,Player_L,Forward,Tottenham,12,8,2760,7.6,Brazilian"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = CsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnMode — position (Forward×5, Midfielder×4, Defender×3 → Forward)
        var posMode = doc.GetColumnMode("position");
        Assert.Equal("Forward", posMode);
        Assert.Equal(posMode, doc.GetColumnMode("position")); // consistent

        // GetColumnMode — club (each appears twice → any valid mode)
        var clubMode = doc.GetColumnMode("club");
        Assert.NotNull(clubMode);

        // GetColumnMode — nationality (English×2, Spanish×1, Brazilian×2, ... → English or Brazilian)
        var natMode = doc.GetColumnMode("nationality");
        Assert.NotNull(natMode);

        // GetColumnMedian — goals (sorted: 1,2,2,3,5,6,8,9,12,15,18,20,24 → median=8 or 9 approximately)
        var goalsMedian = doc.GetColumnMedian("goals");
        Assert.True(goalsMedian >= 1);
        Assert.True(goalsMedian <= 24);
        Assert.Equal(goalsMedian, doc.GetColumnMedian("goals"), precision: 2); // consistent

        // GetColumnMedian — rating
        var ratingMedian = doc.GetColumnMedian("rating");
        Assert.True(ratingMedian >= 7.0);
        Assert.True(ratingMedian <= 8.4);

        // GetColumnMedian — minutes_played
        var minsMedian = doc.GetColumnMedian("minutes_played");
        Assert.True(minsMedian >= 2580);
        Assert.True(minsMedian <= 3300);

        // GetColumnTrimmedMean — goals (10% trim removes PL004 24 and PL003 1-2)
        var goalsTrimmed = doc.GetColumnTrimmedMean("goals", 0.1);
        Assert.True(goalsTrimmed >= 1.0);
        Assert.True(goalsTrimmed <= 24.0);
        Assert.Equal(goalsTrimmed, doc.GetColumnTrimmedMean("goals", 0.1), precision: 2); // consistent

        // GetColumnTrimmedMean — rating with 20% trim
        var ratingTrimmed = doc.GetColumnTrimmedMean("rating", 0.2);
        Assert.True(ratingTrimmed >= 7.0);
        Assert.True(ratingTrimmed <= 8.4);

        // AppendRow — two more players
        doc.AppendRow(new[] { "PL013", "Player_M", "Forward", "Arsenal", "28", "4", "2430", "8.7", "Portuguese" });
        doc.AppendRow(new[] { "PL014", "Player_N", "Defender", "ManCity", "0", "1", "3380", "6.9", "Belgian" });
        Assert.Equal(14, doc.RowCount);

        // After append: Forward still mode (6 occurrences)
        Assert.Equal("Forward", doc.GetColumnMode("position"));

        // Median updates
        var newGoalsMedian = doc.GetColumnMedian("goals");
        Assert.True(newGoalsMedian >= 1.0);

        // SaveToFile
        var out1 = TempFile("dogfood_pl_players_out.csv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = CsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnMode("position"), loaded.GetColumnMode("position"));
        Assert.Equal(doc.GetColumnMedian("goals"), loaded.GetColumnMedian("goals"), precision: 2);
        Assert.Equal(doc.GetColumnTrimmedMean("goals", 0.1), loaded.GetColumnTrimmedMean("goals", 0.1), precision: 2);

        // Final save
        var out2 = TempFile("dogfood_pl_players_v2.csv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = CsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.NotNull(loaded2.GetColumnMode("nationality"));
        Assert.True(loaded2.GetColumnMedian("rating") >= 7.0);
        var ex1 = Record.Exception(() => loaded2.GetColumnMode("club"));
        var ex2 = Record.Exception(() => loaded2.GetColumnTrimmedMean("goals", 0.1));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
