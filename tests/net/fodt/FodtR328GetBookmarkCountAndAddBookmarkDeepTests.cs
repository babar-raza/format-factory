// Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R328

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R328: Tests for FodtDocument.GetBookmarkCount, AddBookmark, GetBookmarkName deeper.
/// GetBookmarkCount(): returns the number of bookmarks in the document.
/// AddBookmark(paragraphIndex, name): adds a named bookmark anchored to the specified paragraph.
/// GetBookmarkName(index): returns the name of the bookmark at the given index.
/// Covers: GetBookmarkCount no-throw; GetBookmarkCount non-negative; GetBookmarkCount consistent;
/// GetBookmarkCount zero for new doc; GetBookmarkCount after AddBookmark increases;
/// GetBookmarkCount save-load;
/// AddBookmark no-throw; AddBookmark increases count; AddBookmark save-load;
/// AddBookmark multiple; AddBookmark then ExportToHtml no-throw;
/// AddBookmark then ExportToMarkdown no-throw; AddBookmark then GetCharCount positive;
/// GetBookmarkName no-throw; GetBookmarkName non-null; GetBookmarkName consistent;
/// GetBookmarkName save-load;
/// dogfood CreateDoc→AddBookmark→GetBookmarkCount→GetBookmarkName→SaveToFile pipeline.
/// </summary>
public class FodtR328GetBookmarkCountAndAddBookmarkDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR328GetBookmarkCountAndAddBookmarkDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR328_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateLegalDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Service Level Agreement: Cloud Infrastructure and Managed Security Operations", 1);
        doc.AppendParagraph("This Service Level Agreement (SLA) governs the provision of cloud infrastructure services and managed security operations between the Service Provider and Customer.");
        doc.AppendParagraph("The Customer shall receive dedicated account management, 24/7 network operations centre support, and guaranteed response times as defined in Schedule 1.");
        doc.InsertHeading(3, "Availability Commitments", 2);
        doc.AppendParagraph("The Service Provider commits to 99.95% monthly uptime for all production workloads, measured as the percentage of minutes per calendar month excluding planned maintenance windows.");
        doc.AppendParagraph("Planned maintenance windows are limited to 4 hours per month, scheduled during agreed low-traffic periods with 14 days prior written notice to the Customer.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetBookmarkCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkCount_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetBookmarkCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkCount_NonNegative()
    {
        var doc = CreateLegalDoc();
        Assert.True(doc.GetBookmarkCount() >= 0);
    }

    [Fact]
    public void GetBookmarkCount_Consistent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with no bookmarks.");
        Assert.Equal(0, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_AfterAddBookmark_Increases()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(1, "bkm:definitions");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void GetBookmarkCount_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "bkm:account-management");
        var before = doc.GetBookmarkCount();
        var path = TempFile("bc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    // -------------------------------------------------------------------------
    // AddBookmark
    // -------------------------------------------------------------------------

    [Fact]
    public void AddBookmark_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.AddBookmark(0, "bkm:introduction"));
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Increases_Count()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetBookmarkCount();
        doc.AddBookmark(3, "bkm:availability-sla");
        Assert.Equal(before + 1, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_SaveLoad_Persists()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(4, "bkm:maintenance-windows");
        var before = doc.GetBookmarkCount();
        var path = TempFile("abm_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Multiple()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bkm:header");
        doc.AddBookmark(1, "bkm:scope");
        doc.AddBookmark(3, "bkm:uptime-guarantee");
        Assert.Equal(3, doc.GetBookmarkCount());
    }

    [Fact]
    public void AddBookmark_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "bkm:html-test");
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(1, "bkm:md-test");
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddBookmark_Then_GetCharCount_Positive()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bkm:char-count-test");
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetBookmarkName
    // -------------------------------------------------------------------------

    [Fact]
    public void GetBookmarkName_NoThrow()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(1, "bkm:name-test");
        var ex = Record.Exception(() => doc.GetBookmarkName(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetBookmarkName_NonNull()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(2, "bkm:non-null-test");
        Assert.NotNull(doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(0, "bkm:consistency-test");
        Assert.Equal(doc.GetBookmarkName(0), doc.GetBookmarkName(0));
    }

    [Fact]
    public void GetBookmarkName_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        doc.AddBookmark(3, "bkm:save-load-test");
        var path = TempFile("bkn_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.NotNull(loaded.GetBookmarkName(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddBookmark_GetBookmarkCount_GetBookmarkName_SaveToFile_Pipeline()
    {
        // Technical specification — data centre interconnect and WAN optimisation contract
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "WAN Optimisation and Data Centre Interconnect Technical Specification", 1);
        doc.AppendParagraph("Multi-protocol label switching (MPLS) VPN services provide dedicated bandwidth allocation with Quality of Service prioritisation across the enterprise WAN backbone.");
        doc.AppendParagraph("Software-defined WAN (SD-WAN) overlay dynamically routes traffic across MPLS, broadband, and 4G/5G links based on real-time path quality measurements.");

        doc.InsertHeading(3, "Bandwidth and Latency SLAs", 2);
        doc.AppendParagraph("MPLS core links guarantee 99.9% committed information rate (CIR) delivery with maximum latency of 8ms RTT between Tier 1 data centres.");
        doc.AppendParagraph("SD-WAN path selection algorithms implement per-packet load balancing with automatic failover within 50ms of detecting link degradation above defined thresholds.");

        doc.InsertHeading(6, "Security Controls", 2);
        doc.AppendParagraph("All WAN traffic is encrypted using AES-256-GCM with IKEv2 key exchange, providing authenticated encryption with associated data (AEAD) protection.");
        doc.AppendParagraph("Zero trust network access (ZTNA) broker enforces identity-aware access controls for remote user connections to data centre hosted applications.");

        doc.InsertHeading(9, "Monitoring and Reporting", 1);
        doc.AppendParagraph("NetFlow telemetry streams from all CE and PE routers enable real-time traffic analysis and capacity planning with 5-minute granularity in the NOC dashboard.");
        doc.AppendParagraph("Monthly SLA compliance reports include per-link utilisation, latency percentiles, packet loss statistics, and availability calculations for each service tier.");

        Assert.Equal(10, doc.GetParagraphCount());
        Assert.Equal(0, doc.GetBookmarkCount());

        // AddBookmark — document navigation anchors
        doc.AddBookmark(0, "bkm:wan-overview");
        Assert.Equal(1, doc.GetBookmarkCount());

        doc.AddBookmark(1, "bkm:mpls-vpn-description");
        Assert.Equal(2, doc.GetBookmarkCount());

        doc.AddBookmark(3, "bkm:bandwidth-sla");
        Assert.Equal(3, doc.GetBookmarkCount());

        doc.AddBookmark(4, "bkm:sdwan-failover");
        Assert.Equal(4, doc.GetBookmarkCount());

        doc.AddBookmark(5, "bkm:encryption-spec");
        Assert.Equal(5, doc.GetBookmarkCount());

        doc.AddBookmark(7, "bkm:netflow-monitoring");
        Assert.Equal(6, doc.GetBookmarkCount());

        doc.AddBookmark(8, "bkm:sla-reports");
        Assert.Equal(7, doc.GetBookmarkCount());

        // Consistent
        Assert.Equal(doc.GetBookmarkCount(), doc.GetBookmarkCount());

        // GetBookmarkName
        var name0 = doc.GetBookmarkName(0);
        Assert.NotNull(name0);
        Assert.Equal(name0, doc.GetBookmarkName(0)); // consistent

        var name3 = doc.GetBookmarkName(3);
        Assert.NotNull(name3);

        var name6 = doc.GetBookmarkName(6);
        Assert.NotNull(name6);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // ExportToPlainText
        var plain = doc.ExportToPlainText();
        Assert.NotNull(plain);
        Assert.NotEmpty(plain);

        // GetCharCount and GetWordCount
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetWordCount() > 0);

        // SaveToFile
        var path = TempFile("dogfood_wan_spec.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(7, loaded.GetBookmarkCount());
        Assert.True(loaded.GetParagraphCount() > 0);
        Assert.NotNull(loaded.GetBookmarkName(0));
        Assert.NotNull(loaded.GetBookmarkName(6));

        // AddBookmark on loaded
        loaded.AddBookmark(9, "bkm:capacity-planning");
        Assert.Equal(8, loaded.GetBookmarkCount());

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: effective WAN optimisation requires integrated SD-WAN orchestration with MPLS reliability and cloud-native security to support hybrid enterprise workloads.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_wan_spec_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(8, loaded2.GetBookmarkCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.NotNull(loaded2.GetBookmarkName(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddBookmark(0, "bkm:final"));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
