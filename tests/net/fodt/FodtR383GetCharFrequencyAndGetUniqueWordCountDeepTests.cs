// Tests for FodtDocument.GetCharFrequency, GetUniqueWordCount deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R383

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R383: Tests for FodtDocument.GetCharFrequency, GetUniqueWordCount deeper.
/// GetCharFrequency(ch): returns the count of occurrences of the given character in the document text.
/// GetUniqueWordCount(): returns the count of distinct words (case-insensitive) in the document.
/// Covers: GetCharFrequency no-throw; GetCharFrequency non-negative; GetCharFrequency consistent;
/// GetCharFrequency zero for absent char; GetCharFrequency save-load;
/// GetUniqueWordCount no-throw; GetUniqueWordCount positive for non-empty doc;
/// GetUniqueWordCount le GetWordCount; GetUniqueWordCount consistent; GetUniqueWordCount save-load;
/// GetUniqueWordCount increases after AppendParagraph with new words;
/// dogfood CreateDoc→GetCharFrequency→GetUniqueWordCount→SaveToFile pipeline.
/// </summary>
public class FodtR383GetCharFrequencyAndGetUniqueWordCountDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR383GetCharFrequencyAndGetUniqueWordCountDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR383_" + Guid.NewGuid().ToString("N"));
        Directory.CreateDirectory(_tempDir);
    }

    public void Dispose()
    {
        if (Directory.Exists(_tempDir))
            Directory.Delete(_tempDir, recursive: true);
    }

    private string TempFile(string name) => Path.Combine(_tempDir, name);

    private static FodtDocument CreateRichDoc()
    {
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Annual Compliance Report", 1);
        doc.AppendParagraph("The compliance framework ensures that all regulatory requirements are satisfied.");
        doc.AppendParagraph("Annual assessments confirm adherence to applicable standards and guidelines.");
        doc.AppendParagraph("The board has reviewed and approved the compliance programme for the current year.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetCharFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetCharFrequency_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetCharFrequency('e'));
        Assert.Null(ex);
    }

    [Fact]
    public void GetCharFrequency_NonNegative()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetCharFrequency('e') >= 0);
    }

    [Fact]
    public void GetCharFrequency_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetCharFrequency('a'), doc.GetCharFrequency('a'));
    }

    [Fact]
    public void GetCharFrequency_Zero_ForAbsentChar()
    {
        var doc = CreateRichDoc();
        Assert.Equal(0, doc.GetCharFrequency('$')); // unlikely to appear
    }

    [Fact]
    public void GetCharFrequency_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetCharFrequency('e');
        var path = TempFile("cf_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetCharFrequency('e'));
    }

    // -------------------------------------------------------------------------
    // GetUniqueWordCount
    // -------------------------------------------------------------------------

    [Fact]
    public void GetUniqueWordCount_NoThrow()
    {
        var doc = CreateRichDoc();
        var ex = Record.Exception(() => doc.GetUniqueWordCount());
        Assert.Null(ex);
    }

    [Fact]
    public void GetUniqueWordCount_Positive_ForNonEmptyDoc()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetUniqueWordCount() > 0);
    }

    [Fact]
    public void GetUniqueWordCount_Le_GetWordCount()
    {
        var doc = CreateRichDoc();
        Assert.True(doc.GetUniqueWordCount() <= doc.GetWordCount());
    }

    [Fact]
    public void GetUniqueWordCount_Consistent()
    {
        var doc = CreateRichDoc();
        Assert.Equal(doc.GetUniqueWordCount(), doc.GetUniqueWordCount());
    }

    [Fact]
    public void GetUniqueWordCount_SaveLoad_Consistent()
    {
        var doc = CreateRichDoc();
        var before = doc.GetUniqueWordCount();
        var path = TempFile("uwc_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetUniqueWordCount());
    }

    [Fact]
    public void GetUniqueWordCount_Increases_After_AppendParagraph_WithNewWords()
    {
        var doc = CreateRichDoc();
        var before = doc.GetUniqueWordCount();
        doc.AppendParagraph("Xenophilia zymurgy quasar floccinaucinihilipilification."); // all new words
        Assert.True(doc.GetUniqueWordCount() > before);
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetCharFrequency_GetUniqueWordCount_SaveToFile_Pipeline()
    {
        // Legal — UK Supreme Court: Landmark Judgment Analysis
        // Textual analysis of Supreme Court judgment in constitutional law case
        // Character frequency and vocabulary richness metrics for legal corpus analysis

        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "R (Miller) v Secretary of State for Exiting the European Union [2017] UKSC 5 — Judgment Analysis", 1);
        doc.AppendParagraph("The Supreme Court of the United Kingdom delivered its judgment in R (Miller) v Secretary of State for Exiting the European Union on 24 January 2017, holding by a majority of eight to three that an Act of Parliament was required before the Government could give notice under Article 50 of the Treaty on European Union of the United Kingdom's intention to withdraw from the European Union.");

        var cfAfterIntro = doc.GetCharFrequency('e');
        Assert.True(cfAfterIntro >= 0);
        var uwcAfterIntro = doc.GetUniqueWordCount();
        Assert.True(uwcAfterIntro > 0);
        Assert.True(uwcAfterIntro <= doc.GetWordCount());

        // Section 1: Constitutional Background
        doc.InsertSection("1. Constitutional Background");
        doc.InsertHeading(3, "1.1 The Royal Prerogative", 2);
        doc.AppendParagraph("The royal prerogative is a body of customary authority, privilege, and immunity recognised in the United Kingdom as the sole prerogative of the Sovereign and normally exercised by Ministers on the Sovereign's behalf. The constitutional principle of parliamentary sovereignty establishes that Parliament has unlimited power to make or unmake any law and that no other person or body can set aside or override legislation duly passed by Parliament.");
        doc.AppendParagraph("The Divisional Court held that it was not open to the Government to use the royal prerogative to give notification under Article 50 of the Treaty on European Union of the United Kingdom's intention to withdraw from the European Union. The Government appealed to the Supreme Court, contending that it was entitled to act on the basis of existing prerogative powers without prior authorisation from Parliament.");

        var cfE = doc.GetCharFrequency('e');
        var cfT = doc.GetCharFrequency('t');
        Assert.True(cfE > cfAfterIntro); // more 'e' characters after more text
        Assert.True(cfT >= 0);
        Assert.Equal(cfE, doc.GetCharFrequency('e')); // consistent
        Assert.Equal(cfT, doc.GetCharFrequency('t')); // consistent

        // Section 2: The Legal Issues
        doc.InsertSection("2. The Legal Issues");
        doc.InsertHeading(3, "2.1 Primary Issue: Parliamentary Authorisation", 2);
        doc.AppendParagraph("The primary legal issue before the Supreme Court was whether the Government was entitled, without prior authorisation from Parliament, to give notice of the United Kingdom's withdrawal from the European Union pursuant to Article 50 of the Treaty on European Union.");
        doc.AppendParagraph("The majority concluded that ministers could not use prerogative powers to withdraw the United Kingdom from the European Union Treaties because doing so would remove certain rights of UK residents which were part of domestic law by virtue of the European Communities Act 1972. The constitutional principle that Parliament may not be bypassed, combined with the extensive changes to domestic law that withdrawal would require, led the majority to conclude that parliamentary authorisation was necessary.");

        doc.InsertHeading(3, "2.2 Secondary Issue: Scottish Parliament Consent", 2);
        doc.AppendParagraph("The Supreme Court was also asked to consider whether the Scottish Parliament's consent was required before notice under Article 50 could be given. The Court unanimously held that the Scottish Parliament's consent was not legally required, though it acknowledged the Sewel Convention which provides that the UK Parliament will not normally legislate for Scotland without the Scottish Parliament's consent on matters within the Parliament's competence.");

        var uwcAfterSec2 = doc.GetUniqueWordCount();
        Assert.True(uwcAfterSec2 > uwcAfterIntro);
        Assert.True(uwcAfterSec2 <= doc.GetWordCount());
        Assert.Equal(doc.GetUniqueWordCount(), doc.GetUniqueWordCount()); // consistent

        // Section 3: The Court's Reasoning
        doc.InsertSection("3. The Court's Reasoning");
        doc.InsertHeading(3, "3.1 Sovereignty of Parliament", 2);
        doc.AppendParagraph("The majority judgment, delivered by Lord Neuberger PSC, Lady Hale DPSC, Lord Mance, Lord Kerr, Lord Clarke, Lord Wilson, Lord Sumption, and Lord Hodge JJSC, affirmed that parliamentary sovereignty remained the fundamental principle of the United Kingdom's constitution. The Court held that the 1972 Act had fundamentally changed the constitutional landscape by making EU law part of domestic law, and that withdrawal from the EU would remove these EU-derived rights from domestic law without the authority of Parliament.");

        // Character frequency for common letters
        var cfEFinal = doc.GetCharFrequency('e');
        var cfAFinal = doc.GetCharFrequency('a');
        var cfIFinal = doc.GetCharFrequency('i');
        var cfNFinal = doc.GetCharFrequency('n');
        Assert.True(cfEFinal > 0);
        Assert.True(cfAFinal > 0);
        Assert.True(cfIFinal > 0);
        Assert.True(cfNFinal > 0);

        // 'z' should be rare (or absent) in legal text
        var cfZ = doc.GetCharFrequency('z');
        Assert.True(cfZ >= 0);
        Assert.True(cfZ < cfEFinal); // 'z' much less frequent than 'e' in legal English

        // '&' should not appear (formal legal writing uses 'and')
        Assert.Equal(0, doc.GetCharFrequency('&'));

        var uwcFinal = doc.GetUniqueWordCount();
        Assert.True(uwcFinal > uwcAfterSec2);
        Assert.True(uwcFinal <= doc.GetWordCount());

        // Basic content checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // SaveToFile
        var path1 = TempFile("dogfood_uksc_miller_analysis.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(cfEFinal, loaded.GetCharFrequency('e'));
        Assert.Equal(cfAFinal, loaded.GetCharFrequency('a'));
        Assert.Equal(uwcFinal, loaded.GetUniqueWordCount());
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Extend with dissenting judgment section
        loaded.InsertSection("4. Dissenting Judgment");
        loaded.InsertHeading(3, "4.1 Lord Reed's Dissent", 2);
        loaded.AppendParagraph("Lord Reed, Lord Carnwath, and Lord Hughes dissented, holding that the Government was entitled to exercise prerogative powers to give notice under Article 50. Lord Reed's dissent emphasised that the 1972 Act was a constitutional statute whose effect was to introduce EU law into domestic law, but that it did not preclude the Government from exercising prerogative powers to withdraw from the EU Treaties themselves, as distinct from the domestic legal consequences which Parliament would then need to address.");

        var cfEAfterDissent = loaded.GetCharFrequency('e');
        Assert.True(cfEAfterDissent > cfEFinal); // more text → more 'e's
        var uwcAfterDissent = loaded.GetUniqueWordCount();
        Assert.True(uwcAfterDissent >= uwcFinal);

        // Final save
        var path2 = TempFile("dogfood_uksc_miller_analysis_final.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(cfEAfterDissent, final.GetCharFrequency('e'));
        Assert.Equal(uwcAfterDissent, final.GetUniqueWordCount());

        Assert.True(final.GetWordCount() > doc.GetWordCount());

        var ex1 = Record.Exception(() => final.GetCharFrequency('a'));
        var ex2 = Record.Exception(() => final.GetUniqueWordCount());
        Assert.Null(ex1);
        Assert.Null(ex2);
    }
}
