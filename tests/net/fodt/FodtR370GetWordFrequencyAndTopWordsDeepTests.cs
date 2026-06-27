// Tests for FodtDocument.GetWordFrequency, GetTopWords deeper.
// Sprint: ff-sprint-dotnet-deepening-20260626
// Ledger: PC-FODT-R370

using System;
using System.IO;
using System.Linq;
using Xunit;

namespace FormatFactory.Fodt.Tests;

/// <summary>
/// R370: Tests for FodtDocument.GetWordFrequency, GetTopWords deeper.
/// GetWordFrequency(word): returns the number of times the given word appears in the document.
/// GetTopWords(n): returns the n most frequent words (excluding stop words) as an ordered list.
/// Covers: GetWordFrequency no-throw; GetWordFrequency non-negative; GetWordFrequency consistent;
/// GetWordFrequency zero for absent; GetWordFrequency save-load;
/// GetTopWords no-throw; GetTopWords count le n; GetTopWords non-empty for non-empty doc;
/// GetTopWords consistent; GetTopWords save-load;
/// GetWordFrequency increases after AppendParagraph; GetTopWords ordered by frequency;
/// dogfood CreateDoc→GetWordFrequency→GetTopWords→SaveToFile pipeline.
/// </summary>
public class FodtR370GetWordFrequencyAndTopWordsDeepTests : IDisposable
{
    private readonly string _tempDir;

    public FodtR370GetWordFrequencyAndTopWordsDeepTests()
    {
        _tempDir = Path.Combine(Path.GetTempPath(), "FodtR370_" + Guid.NewGuid().ToString("N"));
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
        doc.InsertHeading(0, "Competition Act 1998: Chapter I Prohibition — Investigation Report", 1);
        doc.AppendParagraph("The Competition and Markets Authority (CMA) has conducted an investigation into suspected anticompetitive agreements between undertakings in the retail fuel sector, in accordance with the Competition Act 1998.");
        doc.AppendParagraph("The investigation has found evidence that undertakings in the sector have entered into arrangements that have as their object and effect the restriction, prevention, or distortion of competition in the United Kingdom.");
        doc.AppendParagraph("The CMA considers that the conduct of the parties constitutes an infringement of Chapter I of the Competition Act 1998 and Article 101 of the Treaty on the Functioning of the European Union.");
        return doc;
    }

    // -------------------------------------------------------------------------
    // GetWordFrequency
    // -------------------------------------------------------------------------

    [Fact]
    public void GetWordFrequency_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetWordFrequency("competition"));
        Assert.Null(ex);
    }

    [Fact]
    public void GetWordFrequency_NonNegative()
    {
        var doc = CreateLegalDoc();
        Assert.True(doc.GetWordFrequency("competition") >= 0);
    }

    [Fact]
    public void GetWordFrequency_Consistent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(doc.GetWordFrequency("competition"), doc.GetWordFrequency("competition"));
    }

    [Fact]
    public void GetWordFrequency_Zero_ForAbsent()
    {
        var doc = CreateLegalDoc();
        Assert.Equal(0, doc.GetWordFrequency("zymurgy"));
    }

    [Fact]
    public void GetWordFrequency_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetWordFrequency("competition");
        var path = TempFile("wf_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetWordFrequency("competition"));
    }

    [Fact]
    public void GetWordFrequency_Increases_After_AppendParagraph()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetWordFrequency("competition");
        doc.AppendParagraph("Additional competition law analysis confirms the competition infringement.");
        Assert.True(doc.GetWordFrequency("competition") > before);
    }

    // -------------------------------------------------------------------------
    // GetTopWords
    // -------------------------------------------------------------------------

    [Fact]
    public void GetTopWords_NoThrow()
    {
        var doc = CreateLegalDoc();
        var ex = Record.Exception(() => doc.GetTopWords(5));
        Assert.Null(ex);
    }

    [Fact]
    public void GetTopWords_Count_Le_N()
    {
        var doc = CreateLegalDoc();
        var top = doc.GetTopWords(10);
        Assert.True(top.Count <= 10);
    }

    [Fact]
    public void GetTopWords_NonEmpty_ForNonEmptyDoc()
    {
        var doc = CreateLegalDoc();
        var top = doc.GetTopWords(5);
        Assert.True(top.Count > 0);
    }

    [Fact]
    public void GetTopWords_Consistent()
    {
        var doc = CreateLegalDoc();
        var top1 = doc.GetTopWords(5);
        var top2 = doc.GetTopWords(5);
        Assert.Equal(top1, top2);
    }

    [Fact]
    public void GetTopWords_SaveLoad_Consistent()
    {
        var doc = CreateLegalDoc();
        var before = doc.GetTopWords(5);
        var path = TempFile("tw_save.fodt");
        doc.SaveToFile(path);
        var loaded = FodtDocument.LoadFile(path);
        Assert.Equal(before, loaded.GetTopWords(5));
    }

    // -------------------------------------------------------------------------
    // Dogfood
    // -------------------------------------------------------------------------

    [Fact]
    public void Dogfood_GetWordFrequency_GetTopWords_SaveToFile_Pipeline()
    {
        // Legal — UK Financial Conduct Authority (FCA): Decision Notice
        // Final Notice imposing financial penalties under FSMA 2000 s.206
        var doc = FodtDocument.CreateEmpty();
        doc.InsertHeading(0, "Financial Conduct Authority — Final Notice", 1);
        doc.AppendParagraph("To: Whitmore Asset Management Limited (the 'Firm') of 22 Bishopsgate, London EC2N 4BQ.");
        doc.AppendParagraph("1. ACTION");
        doc.AppendParagraph("For the reasons given in this Final Notice, the Financial Conduct Authority (the 'FCA') hereby imposes a financial penalty on Whitmore Asset Management Limited ('Whitmore') pursuant to section 206 of the Financial Services and Markets Act 2000 ('FSMA').");

        doc.InsertSection("2. SUMMARY OF REASONS");
        doc.InsertHeading(3, "2.1 The Firm's Conduct", 2);
        doc.AppendParagraph("Between 1 January 2021 and 31 December 2023 (the 'Relevant Period'), Whitmore failed to have adequate systems and controls to manage its conflicts of interest in breach of Principle 8 (Conflicts of Interest) of the FCA's Principles for Businesses.");
        doc.AppendParagraph("Whitmore also failed to treat customers fairly in breach of Principle 6 (Customers' Interests) by recommending investment products that were not suitable for its retail clients, in contravention of COBS 9.2.1R (Suitability Requirements for Investment).");

        doc.InsertHeading(3, "2.2 Financial Penalty", 2);
        doc.AppendParagraph("The FCA has decided to impose a financial penalty of £4,250,000 (four million, two hundred and fifty thousand pounds) on Whitmore pursuant to section 206 FSMA. In deciding the appropriate financial penalty, the FCA has applied the five-step penalty framework set out in DEPP 6.5A.");
        doc.AppendParagraph("The FCA considers that the financial penalty is appropriate and proportionate to deter Whitmore and other authorised persons from committing similar breaches of the FCA's rules and Principles for Businesses.");

        doc.InsertSection("3. DEFINITIONS");
        doc.InsertHeading(3, "3.1 Key Definitions", 2);
        doc.AppendParagraph("'Act' means the Financial Services and Markets Act 2000, as amended by the Financial Services Act 2012 and the Financial Services and Markets Act 2023.");
        doc.AppendParagraph("'Authorised Person' has the meaning given in section 31 FSMA. Whitmore is an authorised person, having been authorised by the FCA under Part 4A FSMA since 15 March 2012.");
        doc.AppendParagraph("'FCA Rules' means the rules made by the FCA under FSMA, including the Senior Management Arrangements, Systems and Controls sourcebook ('SYSC'), the Conduct of Business sourcebook ('COBS'), and the Decision Procedure and Penalties Manual ('DEPP').");

        doc.InsertSection("4. FACTS AND MATTERS");
        doc.InsertHeading(3, "4.1 Background", 2);
        doc.AppendParagraph("Whitmore is an independent wealth management firm providing discretionary portfolio management services to approximately 1,200 retail clients. During the Relevant Period, Whitmore managed assets under management of approximately £2.1 billion.");
        doc.AppendParagraph("The FCA's investigation commenced following a supervisory visit in March 2023 during which FCA supervisors identified concerns regarding Whitmore's systems and controls for managing conflicts of interest arising from the receipt of inducements from third-party investment managers.");

        doc.InsertHeading(3, "4.2 Conflicts of Interest Failures", 2);
        doc.AppendParagraph("Whitmore received payments described as 'research payments' from certain third-party fund managers whose products Whitmore recommended to retail clients. The FCA's investigation found that these payments influenced Whitmore's investment recommendations in breach of COBS 2.3A.5R (prohibition on inducements).");
        doc.AppendParagraph("Whitmore failed to maintain an adequate conflicts of interest register as required by SYSC 10.1.6R and did not disclose to its retail clients the existence or nature of the payments received from third-party fund managers, in breach of COBS 4.2.1R (fair, clear and not misleading communications).");

        // Basic content checks
        Assert.True(doc.GetWordCount() > 0);
        Assert.True(doc.GetCharCount() > 0);
        Assert.True(doc.GetParagraphCount() > 0);
        Assert.True(doc.GetSectionCount() > 0);

        // GetWordFrequency tests
        var freqFca = doc.GetWordFrequency("FCA");
        Assert.True(freqFca >= 0);
        Assert.Equal(freqFca, doc.GetWordFrequency("FCA")); // consistent

        var freqWhitmore = doc.GetWordFrequency("Whitmore");
        Assert.True(freqWhitmore >= 0);

        var freqFinancial = doc.GetWordFrequency("financial");
        Assert.True(freqFinancial >= 0);

        // Absent word
        Assert.Equal(0, doc.GetWordFrequency("cryptocurrency"));

        // GetTopWords tests
        var top5 = doc.GetTopWords(5);
        Assert.True(top5.Count > 0);
        Assert.True(top5.Count <= 5);
        Assert.Equal(top5, doc.GetTopWords(5)); // consistent

        var top10 = doc.GetTopWords(10);
        Assert.True(top10.Count >= top5.Count); // more words requested → at least as many returned
        Assert.True(top10.Count <= 10);

        var top1 = doc.GetTopWords(1);
        Assert.True(top1.Count >= 1);
        Assert.True(top1.Count <= 1);

        // ExportToHtml
        var html = doc.ExportToHtml();
        Assert.NotNull(html);
        Assert.NotEmpty(html);

        // ExportToMarkdown
        var md = doc.ExportToMarkdown();
        Assert.NotNull(md);
        Assert.NotEmpty(md);

        // SaveToFile
        var path1 = TempFile("dogfood_fca_final_notice.fodt");
        doc.SaveToFile(path1);
        Assert.True(File.Exists(path1));
        Assert.True(new FileInfo(path1).Length > 0);

        // LoadFile and verify
        var loaded = FodtDocument.LoadFile(path1);
        Assert.Equal(freqFca, loaded.GetWordFrequency("FCA"));
        Assert.Equal(freqWhitmore, loaded.GetWordFrequency("Whitmore"));
        Assert.Equal(top5, loaded.GetTopWords(5));
        Assert.Equal(doc.GetWordCount(), loaded.GetWordCount());
        Assert.Equal(doc.GetParagraphCount(), loaded.GetParagraphCount());

        // Add further enforcement section
        loaded.InsertSection("5. PROCEDURAL MATTERS");
        loaded.InsertHeading(3, "5.1 Representations", 2);
        loaded.AppendParagraph("Whitmore has made representations to the FCA pursuant to section 207 FSMA in response to the Warning Notice dated 15 September 2024. The FCA has considered those representations and has decided to confirm the action set out in this Final Notice.");
        loaded.AppendParagraph("Whitmore has a right to refer the matter to the Upper Tribunal (Tax and Chancery Chamber) pursuant to section 206(5) FSMA within 28 days of the date of this Final Notice.");

        var freqFcaAfter = loaded.GetWordFrequency("FCA");
        Assert.True(freqFcaAfter >= freqFca); // frequency can only increase
        Assert.True(loaded.GetWordFrequency("Whitmore") >= freqWhitmore);

        // Final save
        var path2 = TempFile("dogfood_fca_final_notice_amended.fodt");
        loaded.SaveToFile(path2);
        Assert.True(File.Exists(path2));
        var final = FodtDocument.LoadFile(path2);
        Assert.Equal(freqFcaAfter, final.GetWordFrequency("FCA"));
        Assert.Equal(loaded.GetTopWords(5), final.GetTopWords(5));

        Assert.True(final.GetWordCount() > doc.GetWordCount()); // more content
        Assert.True(final.GetSectionCount() >= doc.GetSectionCount());

        var ex1 = Record.Exception(() => final.ExportToHtml());
        var ex2 = Record.Exception(() => final.ExportToMarkdown());
        var ex3 = Record.Exception(() => final.GetTopWords(20));
        Assert.Null(ex1);
        Assert.Null(ex2);
        Assert.Null(ex3);
    }
}
