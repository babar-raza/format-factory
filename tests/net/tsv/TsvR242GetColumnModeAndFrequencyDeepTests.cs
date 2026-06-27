// Tests for TsvDocument.GetColumnMode, GetColumnFrequency, GetColumnUniqueRatio deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R242

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R242: Tests for TsvDocument.GetColumnMode, GetColumnFrequency, GetColumnUniqueRatio deeper.
/// GetColumnMode(columnName): returns the most frequently occurring value in the column.
/// GetColumnFrequency(columnName, value): returns how many times the given value appears.
/// GetColumnUniqueRatio(columnName): returns the ratio of unique values to total values (0–1).
/// Covers: GetColumnMode no-throw; GetColumnMode non-null; GetColumnMode consistent;
/// GetColumnFrequency no-throw; GetColumnFrequency non-negative; GetColumnFrequency consistent;
/// GetColumnFrequency zero for absent value;
/// GetColumnUniqueRatio no-throw; GetColumnUniqueRatio in [0,1]; GetColumnUniqueRatio consistent;
/// GetColumnUniqueRatio one for all-unique column; GetColumnUniqueRatio save-load;
/// dogfood CreateDoc→GetColumnMode→GetColumnFrequency→GetColumnUniqueRatio pipeline.
/// </summary>
public class TsvR242GetColumnModeAndFrequencyDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR242GetColumnModeAndFrequencyDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR242_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateTrainingTsv()
    {
        var path = TempFile("training.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "employee_id\tmodule\tcompletion_status\tpassed\tscore",
            "E001\tCyberSecurity_Awareness\tCompleted\tYes\t92",
            "E002\tCyberSecurity_Awareness\tCompleted\tYes\t78",
            "E003\tCyberSecurity_Awareness\tCompleted\tNo\t45",
            "E004\tGDPR_Foundations\tCompleted\tYes\t88",
            "E005\tGDPR_Foundations\tIn_Progress\tN/A\t0",
            "E006\tCyberSecurity_Awareness\tCompleted\tYes\t95",
            "E007\tManaging_Conduct_Risk\tCompleted\tYes\t82",
            "E008\tCyberSecurity_Awareness\tCompleted\tYes\t76",
            "E009\tGDPR_Foundations\tCompleted\tNo\t52",
            "E010\tManaging_Conduct_Risk\tNot_Started\tN/A\t0",
            "E011\tCyberSecurity_Awareness\tCompleted\tYes\t91",
            "E012\tGDPR_Foundations\tCompleted\tYes\t85",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    private string CreateUniqueIdTsv()
    {
        var path = TempFile("unique_ids.tsv");
        var lines = new System.Collections.Generic.List<string>
        {
            "ref_id\tvalue\tcategory",
            "REF001\t10\tA",
            "REF002\t20\tB",
            "REF003\t30\tA",
            "REF004\t40\tC",
            "REF005\t50\tB",
        };
        File.WriteAllLines(path, lines);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnMode
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnMode_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        var ex = Record.Exception(() => doc.GetColumnMode("module"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnMode_NonNull()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.NotNull(doc.GetColumnMode("module"));
    }

    [Fact]
    public void GetColumnMode_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.Equal(doc.GetColumnMode("completion_status"), doc.GetColumnMode("completion_status"));
    }

    // -------------------------------------------------------------------------
    // GetColumnFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnFrequency_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        var ex = Record.Exception(() => doc.GetColumnFrequency("module", "CyberSecurity_Awareness"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnFrequency_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.True(doc.GetColumnFrequency("module", "GDPR_Foundations") >= 0);
    }

    [Fact]
    public void GetColumnFrequency_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.Equal(
            doc.GetColumnFrequency("completion_status", "Completed"),
            doc.GetColumnFrequency("completion_status", "Completed"));
    }

    [Fact]
    public void GetColumnFrequency_Zero_ForAbsent_Value()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.Equal(0, doc.GetColumnFrequency("module", "NonExistent_Module_XYZ"));
    }

    // -------------------------------------------------------------------------
    // GetColumnUniqueRatio
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniqueRatio_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        var ex = Record.Exception(() => doc.GetColumnUniqueRatio("module"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniqueRatio_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        var ratio = doc.GetColumnUniqueRatio("module");
        Assert.True(ratio >= 0.0 && ratio <= 1.0);
    }

    [Fact]
    public void GetColumnUniqueRatio_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        Assert.Equal(doc.GetColumnUniqueRatio("completion_status"), doc.GetColumnUniqueRatio("completion_status"));
    }

    [Fact]
    public void GetColumnUniqueRatio_One_ForAllUnique()
    {
        var doc = TsvDocument.LoadFile(CreateUniqueIdTsv());
        Assert.Equal(1.0, doc.GetColumnUniqueRatio("ref_id"), precision: 6);
    }

    [Fact]
    public void GetColumnUniqueRatio_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateTrainingTsv());
        var before = doc.GetColumnUniqueRatio("module");
        var path = TempFile("ur_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnUniqueRatio("module"), precision: 6);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnMode_GetColumnFrequency_GetColumnUniqueRatio_Pipeline()
    {
        // Customer service — contact centre call classification and resolution analytics
        var path = TempFile("call_centre.tsv");
        var lines = new System.Collections.Generic.List<string>();
        lines.Add("call_id\tchannel\tcall_type\tresolution\tagent_team\thandle_time_sec\tcsат_score");
        var rng = new Random(20240801);
        string[] channels = { "Phone", "Chat", "Email", "Social_Media" };
        string[] types = { "Billing_Query", "Technical_Support", "Order_Status", "Complaint", "General_Enquiry" };
        string[] resolutions = { "Resolved_FCR", "Escalated", "Callback_Required", "Self_Serve_Redirect" };
        string[] teams = { "Tier1_General", "Tier2_Technical", "Tier1_Billing", "Complaints_Specialist" };
        for (int i = 0; i < 120; i++)
        {
            var ch = channels[i % 4];
            var tp = types[i % 5];
            // Technical_Support and Complaints most often escalated
            var res = (tp == "Technical_Support" && rng.NextDouble() < 0.4) ? "Escalated" :
                      (tp == "Complaint" && rng.NextDouble() < 0.5) ? "Escalated" :
                      resolutions[i % 4];
            var team = teams[i % 4];
            int handle = 120 + rng.Next(0, 480);
            int csat = 1 + rng.Next(0, 5);
            lines.Add($"CALL{i:D5}\t{ch}\t{tp}\t{res}\t{team}\t{handle}\t{csat}");
        }
        File.WriteAllLines(path, lines);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(120, doc.RowCount);

        // GetColumnMode — most common call type and resolution
        var modeType = doc.GetColumnMode("call_type");
        Assert.NotNull(modeType);
        Assert.Equal(modeType, doc.GetColumnMode("call_type")); // consistent

        var modeRes = doc.GetColumnMode("resolution");
        Assert.NotNull(modeRes);

        // GetColumnFrequency — count specific categories
        var phoneCount = doc.GetColumnFrequency("channel", "Phone");
        Assert.True(phoneCount >= 0);
        Assert.Equal(phoneCount, doc.GetColumnFrequency("channel", "Phone")); // consistent

        var billingCount = doc.GetColumnFrequency("call_type", "Billing_Query");
        Assert.True(billingCount >= 0);

        var absentCount = doc.GetColumnFrequency("resolution", "Resolution_Type_Does_Not_Exist");
        Assert.Equal(0, absentCount);

        // GetColumnUniqueRatio — call_id should be fully unique; channel should be ~4/120
        var idRatio = doc.GetColumnUniqueRatio("call_id");
        Assert.Equal(1.0, idRatio, precision: 6);

        var channelRatio = doc.GetColumnUniqueRatio("channel");
        Assert.True(channelRatio > 0 && channelRatio <= 1.0);
        Assert.Equal(channelRatio, doc.GetColumnUniqueRatio("channel")); // consistent

        // All columns
        foreach (var col in new[] { "channel", "call_type", "resolution", "agent_team" })
        {
            Assert.NotNull(doc.GetColumnMode(col));
            Assert.True(doc.GetColumnFrequency(col, "NonExistent") == 0);
            var ratio = doc.GetColumnUniqueRatio(col);
            Assert.True(ratio >= 0 && ratio <= 1.0);
        }

        // SaveToFile
        var outPath = TempFile("call_centre_out.tsv");
        doc.SaveToFile(outPath);
        Assert.True(File.Exists(outPath));

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(outPath);
        Assert.Equal(modeType, loaded.GetColumnMode("call_type"));
        Assert.Equal(phoneCount, loaded.GetColumnFrequency("channel", "Phone"));
        Assert.Equal(idRatio, loaded.GetColumnUniqueRatio("call_id"), precision: 6);
        Assert.Equal(doc.RowCount, loaded.RowCount);

        // GetColumnMean for numeric column
        var meanHandle = doc.GetColumnMean("handle_time_sec");
        Assert.True(meanHandle >= 0);
    }
}
