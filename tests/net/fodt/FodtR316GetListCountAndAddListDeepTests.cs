// Tests for FodtDocument.GetListCount, AddList, GetListItemCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R316

using System;
using System.IO;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R316: Tests for FodtDocument.GetListCount, AddList, GetListItemCount deeper.
/// GetListCount(): returns the number of lists (ordered or unordered) in the document.
/// AddList(items, ordered): adds a list with the given items; ordered=true for numbered list.
/// GetListItemCount(listIndex): returns the number of items in the list at the given index.
/// Covers: GetListCount no-throw; GetListCount non-negative; GetListCount consistent;
/// GetListCount zero for new doc; GetListCount after AddList increases; GetListCount save-load;
/// AddList no-throw; AddList increases count; AddList save-load;
/// AddList ordered and unordered; AddList then ExportToHtml no-throw; AddList then ExportToMarkdown no-throw;
/// AddList then GetCharCount positive;
/// GetListItemCount no-throw; GetListItemCount positive; GetListItemCount consistent;
/// GetListItemCount save-load;
/// dogfood CreateDoc→AddList→GetListCount→GetListItemCount→SaveToFile pipeline.
/// </summary>
public class FodtR316GetListCountAndAddListDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR316GetListCountAndAddListDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR316_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateTechDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "DevOps Pipeline Architecture: Principles and Implementation", 1);
        doc.AppendParagraph("Continuous integration and delivery pipelines automate software build, test, and deployment workflows.");
        doc.AppendParagraph("Infrastructure-as-code practices enable reproducible environment provisioning across development, staging, and production.");
        doc.InsertHeading(3, "Container Orchestration", 2);
        doc.AppendParagraph("Kubernetes provides declarative workload management with automatic scaling, healing, and service discovery.");
        doc.AppendParagraph("Helm charts package Kubernetes manifests with templating support for environment-specific configuration.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetListCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListCount_NoThrow()
    {
        var doc = CreateTechDoc();
        var ex = Record.Exception(() => doc.GetListCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetListCount_NonNegative()
    {
        var doc = CreateTechDoc();
        Assert.True(doc.GetListCount() >= 0);
    }

    [Fact]
    public void GetListCount_Consistent()
    {
        var doc = CreateTechDoc();
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
    }

    [Fact]
    public void GetListCount_Zero_ForNewDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.AppendParagraph("A document with prose but no lists.");
        Assert.Equal(0, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_AfterAddList_Increases()
    {
        var doc = CreateTechDoc();
        var before = doc.GetListCount();
        doc.AddList(new[] { "Plan", "Code", "Build", "Test", "Deploy", "Monitor" }, ordered: true);
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void GetListCount_SaveLoad_Consistent()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "Docker", "Kubernetes", "Helm", "Istio" }, ordered: false);
        var before = doc.GetListCount();
        var path = TempFile("lc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    // -------------------------------------------------------------------------
    // AddList
    // -------------------------------------------------------------------------

    [Fact]
    public void AddList_NoThrow_Ordered()
    {
        var doc = CreateTechDoc();
        var ex = Record.Exception(() => doc.AddList(new[] { "First", "Second", "Third" }, ordered: true));
        Assert.Null(ex);
    }

    [Fact]
    public void AddList_NoThrow_Unordered()
    {
        var doc = CreateTechDoc();
        var ex = Record.Exception(() => doc.AddList(new[] { "Alpha", "Beta", "Gamma" }, ordered: false));
        Assert.Null(ex);
    }

    [Fact]
    public void AddList_Increases_Count()
    {
        var doc = CreateTechDoc();
        var before = doc.GetListCount();
        doc.AddList(new[] { "CI", "CD", "CT" }, ordered: false);
        Assert.Equal(before + 1, doc.GetListCount());
    }

    [Fact]
    public void AddList_SaveLoad_Persists()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "Prometheus", "Grafana", "AlertManager" }, ordered: false);
        var before = doc.GetListCount();
        var path = TempFile("al_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListCount());
    }

    [Fact]
    public void AddList_Multiple()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "Plan", "Build", "Deploy" }, ordered: true);
        doc.AddList(new[] { "Docker", "Podman", "CRI-O" }, ordered: false);
        doc.AddList(new[] { "EKS", "GKE", "AKS", "Rancher" }, ordered: false);
        Assert.Equal(3, doc.GetListCount());
    }

    [Fact]
    public void AddList_Then_ExportToHtml_NoThrow()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "HTML item 1", "HTML item 2" }, ordered: true);
        var ex = Record.Exception(() => doc.ExportToHtml());
        Assert.Null(ex);
    }

    [Fact]
    public void AddList_Then_ExportToMarkdown_NoThrow()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "MD item 1", "MD item 2", "MD item 3" }, ordered: false);
        var ex = Record.Exception(() => doc.ExportToMarkdown());
        Assert.Null(ex);
    }

    [Fact]
    public void AddList_Then_GetCharCount_Positive()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "Item A", "Item B" }, ordered: true);
        Assert.True(doc.GetCharCount() > 0);
    }

    // -------------------------------------------------------------------------
    // GetListItemCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetListItemCount_NoThrow()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "X", "Y", "Z" }, ordered: false);
        var ex = Record.Exception(() => doc.GetListItemCount(0));
        Assert.Null(ex);
    }

    [Fact]
    public void GetListItemCount_Positive()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "Item 1", "Item 2", "Item 3", "Item 4" }, ordered: true);
        Assert.True(doc.GetListItemCount(0) > 0);
    }

    [Fact]
    public void GetListItemCount_Consistent()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "A", "B", "C" }, ordered: false);
        Assert.Equal(doc.GetListItemCount(0), doc.GetListItemCount(0));
    }

    [Fact]
    public void GetListItemCount_SaveLoad_Consistent()
    {
        var doc = CreateTechDoc();
        doc.AddList(new[] { "One", "Two", "Three", "Four", "Five" }, ordered: true);
        var before = doc.GetListItemCount(0);
        var path = TempFile("lic_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetListItemCount(0));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_AddList_GetListCount_GetListItemCount_SaveToFile_Pipeline()
    {
        // Technical policy document — cloud security framework
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Cloud Security Framework: Controls, Compliance, and Governance", 1);
        doc.AppendParagraph("Cloud security requires a defence-in-depth architecture spanning identity, network, data, and workload protection layers.");
        doc.AppendParagraph("Zero-trust network architecture eliminates implicit trust and requires explicit verification for every access request.");

        doc.InsertHeading(3, "Identity and Access Management", 2);
        doc.AppendParagraph("Multi-factor authentication reduces account compromise risk by 99.9% according to Microsoft Security Intelligence reports.");

        doc.InsertHeading(6, "Data Protection", 2);
        doc.AppendParagraph("Encryption at rest and in transit protects data confidentiality across storage, compute, and network boundaries.");
        doc.AppendParagraph("Key management services provide centralised control over cryptographic material lifecycle.");

        doc.InsertHeading(9, "Compliance and Audit", 1);
        doc.AppendParagraph("Continuous compliance monitoring detects configuration drift from security baselines in real time.");

        // Initial list count — zero
        Assert.Equal(0, doc.GetListCount());

        // AddList — ordered: IAM implementation steps
        doc.AddList(new[] {
            "Enable MFA for all administrative accounts",
            "Implement least-privilege role assignments",
            "Configure conditional access policies",
            "Enable privileged identity management (PIM)",
            "Deploy identity protection with risk-based policies"
        }, ordered: true);
        Assert.Equal(1, doc.GetListCount());
        Assert.Equal(5, doc.GetListItemCount(0));

        // AddList — unordered: network security controls
        doc.AddList(new[] {
            "Web Application Firewall (WAF)",
            "DDoS protection service",
            "Network Security Groups (NSG)",
            "Private endpoints for PaaS services",
            "VPN Gateway or ExpressRoute connectivity",
            "Azure Bastion for secure RDP/SSH access"
        }, ordered: false);
        Assert.Equal(2, doc.GetListCount());
        Assert.Equal(6, doc.GetListItemCount(1));

        // AddList — ordered: data classification tiers
        doc.AddList(new[] {
            "Public — no controls required",
            "Internal — basic access restrictions",
            "Confidential — encryption and logging mandatory",
            "Highly Confidential — MFA + DLP + audit trail required"
        }, ordered: true);
        Assert.Equal(3, doc.GetListCount());
        Assert.Equal(4, doc.GetListItemCount(2));

        // AddList — unordered: compliance frameworks
        doc.AddList(new[] {
            "ISO 27001 — Information Security Management",
            "SOC 2 Type II — Service Organisation Controls",
            "GDPR — General Data Protection Regulation",
            "PCI-DSS — Payment Card Industry Standards",
            "NIST CSF — Cybersecurity Framework",
            "CIS Controls v8 — Critical Security Controls"
        }, ordered: false);
        Assert.Equal(4, doc.GetListCount());
        Assert.Equal(6, doc.GetListItemCount(3));

        // Consistent
        Assert.Equal(doc.GetListCount(), doc.GetListCount());
        Assert.Equal(doc.GetListItemCount(0), doc.GetListItemCount(0));

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
        var path = TempFile("dogfood_cloud_security.fodt");
        doc.SaveToFile(path);
        Assert.True(File.Exists(path));
        Assert.True(new FileInfo(path).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(4, loaded.GetListCount());
        Assert.Equal(5, loaded.GetListItemCount(0));
        Assert.Equal(6, loaded.GetListItemCount(1));
        Assert.Equal(4, loaded.GetListItemCount(2));
        Assert.Equal(6, loaded.GetListItemCount(3));
        Assert.True(loaded.GetParagraphCount() > 0);

        // AddList on loaded
        loaded.AddList(new[] {
            "Incident detection and alerting",
            "Containment and isolation procedures",
            "Evidence preservation and forensics",
            "Recovery and lessons-learned review"
        }, ordered: true);
        Assert.Equal(5, loaded.GetListCount());
        Assert.Equal(4, loaded.GetListItemCount(4));

        // ExportToHtml on loaded
        var loadedHtml = loaded.ExportToHtml();
        Assert.NotNull(loadedHtml);
        Assert.NotEmpty(loadedHtml);

        // AppendParagraph on loaded
        loaded.AppendParagraph("Conclusion: effective cloud security requires continuous governance, automation, and a culture of shared responsibility.");
        Assert.True(loaded.GetParagraphCount() > doc.GetParagraphCount());

        // Final save
        var path2 = TempFile("dogfood_cloud_security_v2.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var loaded2 = FodtDocument.LoadFile(path2);
        Assert.Equal(5, loaded2.GetListCount());
        Assert.True(loaded2.GetParagraphCount() > 0);
        Assert.Equal(5, loaded2.GetListItemCount(0));
        var ex1 = Record.Exception(() => loaded2.ExportToHtml());
        var ex2 = Record.Exception(() => loaded2.ExportToMarkdown());
        var ex3 = Record.Exception(() => loaded2.AddList(new[] { "New item" }, ordered: false));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
