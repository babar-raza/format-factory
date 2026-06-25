// Tests for TxtWriter.WriteLines() edge cases: CRLF normalization, all-null inputs,
// large line counts, and single-line boundary behaviors.
// Sprint: FORMAT-FACTORY-TXT-WRITER-R119-20260626
// Ledger: R119-GOVERNED-DOTNET-TXT-WRITELINES-EDGECASES-001

using System;
using System.Collections.Generic;
using System.Linq;
using Xunit;

namespace FormatFactory.Txt.Tests;

/// <summary>
/// R119: TxtWriter.WriteLines() edge cases — CRLF and bare-CR in input lines are normalized
/// to LF in output, all-null list produces correct separator output, large line counts
/// produce correct newline counts, empty string entries preserved as-is.
/// </summary>
public class TxtR119WriteLinesEdgeCasesTests
{
    // ---- CRLF normalization ----

    [Fact]
    public void WriteLines_InputContainsCrLf_NormalizedToLf()
    {
        var result = TxtWriter.WriteLines(new[] { "line A\r\nline A cont", "line B" });
        Assert.DoesNotContain("\r\n", result);
        Assert.Contains("\n", result);
    }

    [Fact]
    public void WriteLines_InputContainsBareCarriageReturn_NormalizedToLf()
    {
        var result = TxtWriter.WriteLines(new[] { "before\rafter", "next" });
        Assert.DoesNotContain("\r", result);
    }

    [Fact]
    public void WriteLines_AllCrLfInput_OutputContainsNoCarriageReturns()
    {
        var lines = new[] { "alpha\r\nbeta", "gamma\r\ndelta" };
        var result = TxtWriter.WriteLines(lines);
        Assert.DoesNotContain("\r", result);
    }

    // ---- All-null input ----

    [Fact]
    public void WriteLines_AllNullEntries_ProducesNewlineSeparators()
    {
        // Three nulls: "", "", "" joined by "\n" → "\n\n"
        var result = TxtWriter.WriteLines(new string?[] { null, null, null });
        Assert.Equal("\n\n", result);
    }

    [Fact]
    public void WriteLines_SingleNullEntry_ProducesEmptyString()
    {
        var result = TxtWriter.WriteLines(new string?[] { null });
        Assert.Equal(string.Empty, result);
    }

    // ---- Empty string entries (not null) ----

    [Fact]
    public void WriteLines_EmptyStringEntry_PreservedAsSeparatorLine()
    {
        // Empty string is the same as null in this context
        var result = TxtWriter.WriteLines(new[] { "before", string.Empty, "after" });
        Assert.Contains("before", result);
        Assert.Contains("after", result);
        Assert.Contains("\n\n", result);
    }

    // ---- Large line count ----

    [Fact]
    public void WriteLines_HundredLines_NinetyNineNewlines()
    {
        var lines = Enumerable.Range(1, 100).Select(i => $"Line {i:D3}").ToList();
        var result = TxtWriter.WriteLines(lines);
        var newlineCount = result.Count(c => c == '\n');
        Assert.Equal(99, newlineCount);
    }

    [Fact]
    public void WriteLines_HundredLines_AllLinesPresent()
    {
        var lines = Enumerable.Range(1, 100).Select(i => $"Entry{i}").ToList();
        var result = TxtWriter.WriteLines(lines);
        Assert.Contains("Entry1",   result);
        Assert.Contains("Entry50",  result);
        Assert.Contains("Entry100", result);
    }

    // ---- Boundary: single line ----

    [Fact]
    public void WriteLines_SingleNonEmptyLine_NoNewlineInResult()
    {
        var result = TxtWriter.WriteLines(new[] { "only line" });
        Assert.Equal("only line", result);
        Assert.DoesNotContain("\n", result);
    }

    // ---- Unicode content ----

    [Fact]
    public void WriteLines_UnicodeContent_PreservedInOutput()
    {
        var result = TxtWriter.WriteLines(new[] { "Résumé", "日本語", "العربية" });
        Assert.Contains("Résumé",   result);
        Assert.Contains("日本語",   result);
        Assert.Contains("العربية", result);
    }

    // ---- Dogfood: log file generation pipeline ----

    [Fact]
    public void DogfoodPipeline_LogFileGeneration_AllEntriesAndFormatCorrect()
    {
        var timestamp = "2026-06-27T04:45:00Z";
        var logEntries = new List<string?>
        {
            $"[INFO]  {timestamp} Sprint S106 started",
            $"[INFO]  {timestamp} Processing work item WI-S106-001",
            $"[DEBUG] {timestamp} File created: tests/net/txt/TxtR119WriteLinesEdgeCasesTests.cs",
            $"[INFO]  {timestamp} Work item WI-S106-001 completed",
            null,                                                           // blank separator line
            $"[INFO]  {timestamp} Processing work item WI-S106-002",
            $"[DEBUG] {timestamp} File created: tests/net/html/HtmlR119TableEdgeCasesTests.cs",
            $"[INFO]  {timestamp} Work item WI-S106-002 completed",
            null,                                                           // blank separator line
            $"[INFO]  {timestamp} Sprint S106 complete. Exit 0.",
        };

        var output = TxtWriter.WriteLines(logEntries);

        // Content checks
        Assert.Contains("Sprint S106 started",   output);
        Assert.Contains("WI-S106-001 completed", output);
        Assert.Contains("WI-S106-002 completed", output);
        Assert.Contains("Sprint S106 complete",  output);

        // Encoding checks
        Assert.DoesNotContain("\r\n", output);
        Assert.Contains("\n\n", output); // blank separator lines
    }
}
