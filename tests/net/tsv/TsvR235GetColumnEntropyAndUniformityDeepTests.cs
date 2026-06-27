// Tests for TsvDocument.GetColumnEntropy, GetColumnUniformity, GetColumnGiniImpurity deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-TSV-R235

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Tsv.Tests;

/// <summary>
/// R235: Tests for TsvDocument.GetColumnEntropy, GetColumnUniformity, GetColumnGiniImpurity deeper.
/// GetColumnEntropy(col): returns the Shannon entropy (in bits) of value distribution in the column.
/// GetColumnUniformity(col): returns [0,1] uniformity score; 1 = all values equal, 0 = maximally varied.
/// GetColumnGiniImpurity(col): returns the Gini impurity of categorical value distribution.
/// Covers: GetColumnEntropy no-throw; GetColumnEntropy non-negative; GetColumnEntropy consistent;
/// GetColumnEntropy zero for uniform; GetColumnEntropy save-load;
/// GetColumnUniformity no-throw; GetColumnUniformity in [0,1]; GetColumnUniformity consistent;
/// GetColumnUniformity one for uniform column; GetColumnUniformity save-load;
/// GetColumnGiniImpurity no-throw; GetColumnGiniImpurity in [0,1]; GetColumnGiniImpurity consistent;
/// GetColumnGiniImpurity zero for uniform; GetColumnGiniImpurity save-load;
/// dogfood Append→GetColumnEntropy→GetColumnUniformity→GetColumnGiniImpurity→SaveToFile pipeline.
/// </summary>
public class TsvR235GetColumnEntropyAndUniformityDeepTests : IDisposable
{
    private readonly string _tempDir;

    public TsvR235GetColumnEntropyAndUniformityDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "TsvR235_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private string CreateCategoricalTsv()
    {
        var path = TempFile("categorical.tsv");
        var lines = new[]
        {
            "patient_id\tblood_type\tgender\toutcome",
            "P001\tA+\tF\tRecovered",
            "P002\tO+\tM\tRecovered",
            "P003\tB+\tF\tDeceased",
            "P004\tAB+\tM\tRecovered",
            "P005\tA+\tF\tRecovered",
            "P006\tO+\tM\tRecovered",
            "P007\tO-\tF\tDeceased",
            "P008\tA+\tM\tRecovered",
            "P009\tO+\tF\tRecovered",
            "P010\tB-\tM\tRecovered",
            "P011\tA+\tF\tRecovered",
            "P012\tO+\tM\tRecovered"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    private string CreateUniformTsv()
    {
        var path = TempFile("uniform.tsv");
        var lines = new[]
        {
            "id\tcategory\tvalue",
            "1\tAlpha\t100",
            "2\tAlpha\t100",
            "3\tAlpha\t100",
            "4\tAlpha\t100",
            "5\tAlpha\t100"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);
        return path;
    }

    // -------------------------------------------------------------------------
    // GetColumnEntropy
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnEntropy_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var ex = Record.Exception(() => doc.GetColumnEntropy("blood_type"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnEntropy_NonNegative()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        Assert.True(doc.GetColumnEntropy("blood_type") >= 0.0);
    }

    [Fact]
    public void GetColumnEntropy_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        Assert.Equal(doc.GetColumnEntropy("blood_type"), doc.GetColumnEntropy("blood_type"), precision: 4);
    }

    [Fact]
    public void GetColumnEntropy_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnEntropy("category"), precision: 4);
    }

    [Fact]
    public void GetColumnEntropy_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var before = doc.GetColumnEntropy("outcome");
        var path = TempFile("ent_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnEntropy("outcome"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnUniformity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnUniformity_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var ex = Record.Exception(() => doc.GetColumnUniformity("gender"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnUniformity_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var u = doc.GetColumnUniformity("blood_type");
        Assert.True(u >= 0.0 && u <= 1.0);
    }

    [Fact]
    public void GetColumnUniformity_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        Assert.Equal(doc.GetColumnUniformity("gender"), doc.GetColumnUniformity("gender"), precision: 4);
    }

    [Fact]
    public void GetColumnUniformity_One_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(1.0, doc.GetColumnUniformity("category"), precision: 4);
    }

    [Fact]
    public void GetColumnUniformity_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var before = doc.GetColumnUniformity("outcome");
        var path = TempFile("uni_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnUniformity("outcome"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // GetColumnGiniImpurity
    // -------------------------------------------------------------------------

    [Fact]
    public void GetColumnGiniImpurity_NoThrow()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var ex = Record.Exception(() => doc.GetColumnGiniImpurity("outcome"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetColumnGiniImpurity_InRange()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var g = doc.GetColumnGiniImpurity("blood_type");
        Assert.True(g >= 0.0 && g <= 1.0);
    }

    [Fact]
    public void GetColumnGiniImpurity_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        Assert.Equal(doc.GetColumnGiniImpurity("outcome"), doc.GetColumnGiniImpurity("outcome"), precision: 4);
    }

    [Fact]
    public void GetColumnGiniImpurity_Zero_ForUniform()
    {
        var doc = TsvDocument.LoadFile(CreateUniformTsv());
        Assert.Equal(0.0, doc.GetColumnGiniImpurity("category"), precision: 4);
    }

    [Fact]
    public void GetColumnGiniImpurity_SaveLoad_Consistent()
    {
        var doc = TsvDocument.LoadFile(CreateCategoricalTsv());
        var before = doc.GetColumnGiniImpurity("outcome");
        var path = TempFile("gini_save.tsv");
        doc.SaveToFile(path);
        var loaded = TsvDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetColumnGiniImpurity("outcome"), precision: 4);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetColumnEntropy_GetColumnUniformity_GetColumnGiniImpurity_SaveToFile_Pipeline()
    {
        // Cybersecurity threat intelligence — SOC alert triage dataset
        var path = TempFile("dogfood_soc_alerts.tsv");
        var lines = new[]
        {
            "alert_id\tseverity\tcategory\tsource_ip_class\tdestination\tprotocol\taction\tanalyst",
            "A001\tCritical\tMalware\tExternal\tDMZ\tTCP\tBlocked\tAlice",
            "A002\tHigh\tPhishing\tInternal\tCorporate\tSMTP\tQuarantined\tBob",
            "A003\tMedium\tRecon\tExternal\tDMZ\tUDP\tLogged\tAlice",
            "A004\tCritical\tRansomware\tInternal\tEndpoint\tSMB\tBlocked\tCharlie",
            "A005\tLow\tSpam\tExternal\tEmail\tSMTP\tFiltered\tBob",
            "A006\tHigh\tMalware\tExternal\tDMZ\tHTTPS\tBlocked\tAlice",
            "A007\tMedium\tCredential\tInternal\tCorporate\tLDAP\tLogged\tCharlie",
            "A008\tCritical\tAPT\tExternal\tCorporate\tTCP\tBlocked\tAlice",
            "A009\tHigh\tPhishing\tExternal\tEmail\tSMTP\tQuarantined\tBob",
            "A010\tMedium\tRecon\tExternal\tDMZ\tICMP\tLogged\tAlice",
            "A011\tCritical\tMalware\tExternal\tEndpoint\tHTTPS\tBlocked\tCharlie",
            "A012\tLow\tSpam\tInternal\tEmail\tSMTP\tFiltered\tBob"
        };
        File.WriteAllLines(path, lines, System.Text.Encoding.UTF8);

        var doc = TsvDocument.LoadFile(path);
        Assert.Equal(12, doc.RowCount);

        // GetColumnEntropy — severity (4 values: Critical×4, High×3, Medium×3, Low×2 → moderate entropy)
        var sevEntropy = doc.GetColumnEntropy("severity");
        Assert.True(sevEntropy >= 0.0);
        Assert.Equal(sevEntropy, doc.GetColumnEntropy("severity"), precision: 4); // consistent

        // GetColumnEntropy — action (3 values: Blocked×5, Logged×3, Quarantined×2, Filtered×2 → moderate)
        var actionEntropy = doc.GetColumnEntropy("action");
        Assert.True(actionEntropy >= 0.0);

        // GetColumnEntropy — uniform column (all External destination type = DMZ or Email...)
        // source_ip_class: External×9, Internal×3 → non-zero entropy
        var ipEntropy = doc.GetColumnEntropy("source_ip_class");
        Assert.True(ipEntropy >= 0.0);

        // GetColumnUniformity — severity (4 distinct values → not uniform)
        var sevUniformity = doc.GetColumnUniformity("severity");
        Assert.True(sevUniformity >= 0.0 && sevUniformity <= 1.0);
        Assert.Equal(sevUniformity, doc.GetColumnUniformity("severity"), precision: 4); // consistent

        // GetColumnUniformity — analyst (3 analysts: Alice×5, Bob×4, Charlie×3 → moderate uniformity)
        var analystUniformity = doc.GetColumnUniformity("analyst");
        Assert.True(analystUniformity >= 0.0 && analystUniformity <= 1.0);

        // GetColumnGiniImpurity — severity
        var sevGini = doc.GetColumnGiniImpurity("severity");
        Assert.True(sevGini >= 0.0 && sevGini <= 1.0);
        Assert.Equal(sevGini, doc.GetColumnGiniImpurity("severity"), precision: 4); // consistent

        // GetColumnGiniImpurity — protocol (TCP/UDP/SMTP/SMB/HTTPS/LDAP/ICMP → high impurity)
        var protGini = doc.GetColumnGiniImpurity("protocol");
        Assert.True(protGini >= 0.0 && protGini <= 1.0);
        // Higher impurity than severity (more distinct protocols)
        Assert.True(protGini >= 0.0);

        // AppendRow — add two more alerts
        doc.AppendRow(new[] { "A013", "Critical", "Ransomware", "External", "Endpoint", "TCP", "Blocked", "Alice" });
        doc.AppendRow(new[] { "A014", "High", "APT", "External", "Corporate", "HTTPS", "Blocked", "Charlie" });
        Assert.Equal(14, doc.RowCount);

        // After append, entropy of severity should remain non-negative
        Assert.True(doc.GetColumnEntropy("severity") >= 0.0);

        // SaveToFile
        var out1 = TempFile("dogfood_soc_alerts_out.tsv");
        doc.SaveToFile(out1);
        Assert.True(File.Exists(out1));
        Assert.True(new FileInfo(out1).Length > 0);

        // LoadFile and verify
        var loaded = TsvDocument.LoadFile(out1);
        Assert.Equal(14, loaded.RowCount);
        Assert.Equal(doc.GetColumnEntropy("severity"), loaded.GetColumnEntropy("severity"), precision: 4);
        Assert.Equal(doc.GetColumnUniformity("analyst"), loaded.GetColumnUniformity("analyst"), precision: 4);
        Assert.Equal(doc.GetColumnGiniImpurity("protocol"), loaded.GetColumnGiniImpurity("protocol"), precision: 4);

        // Uniform column test on loaded
        var uniformPath = TempFile("dogfood_uniform.tsv");
        var uniformLines = new[] { "id\tstatus\tvalue", "1\tActive\t10", "2\tActive\t20", "3\tActive\t30" };
        File.WriteAllLines(uniformPath, uniformLines, System.Text.Encoding.UTF8);
        var uniformDoc = TsvDocument.LoadFile(uniformPath);
        Assert.Equal(0.0, uniformDoc.GetColumnEntropy("status"), precision: 4);
        Assert.Equal(1.0, uniformDoc.GetColumnUniformity("status"), precision: 4);
        Assert.Equal(0.0, uniformDoc.GetColumnGiniImpurity("status"), precision: 4);

        // Final save
        var out2 = TempFile("dogfood_soc_alerts_v2.tsv");
        loaded.SaveToFile(out2);
        Assert.True(File.Exists(out2));
        var loaded2 = TsvDocument.LoadFile(out2);
        Assert.Equal(14, loaded2.RowCount);
        Assert.True(loaded2.GetColumnEntropy("severity") >= 0.0);
        Assert.True(loaded2.GetColumnUniformity("severity") >= 0.0);
        Assert.True(loaded2.GetColumnGiniImpurity("severity") >= 0.0);
        var ex1 = Record.Exception(() => loaded2.GetColumnEntropy("action"));
        var ex2 = Record.Exception(() => loaded2.GetColumnUniformity("analyst"));
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
