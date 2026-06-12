// AUTH-HARDEN-001: Security and malformed-input tests for FormatFactory.Ndjson

using System.Text;
using System.Text.Json;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonSecurityTests
{
    [Fact]
    public void ReadRecords_DeeplyNestedJson_HandledGracefully()
    {
        // 128 levels of nesting — should either parse or throw NdjsonException, never crash
        var open = new string('[', 128);
        var close = new string(']', 128);
        var input = open + "1" + close + "\n";

        // System.Text.Json has a default max depth of 64; this should throw NdjsonException
        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(input));
        Assert.Contains("line 1", ex.Message);
    }

    [Fact]
    public void ReadRecords_ExtremelyLongLine_ParsesOrThrows()
    {
        // Single JSON line with a 1MB string value
        var longValue = new string('A', 1_000_000);
        var input = $"{{\"data\":\"{longValue}\"}}\n";

        var records = NdjsonReader.ReadRecords(input);
        Assert.Single(records);
        Assert.Equal(longValue, records[0].GetProperty("data").GetString());
    }

    [Fact]
    public void ReadRecords_TruncatedJson_ThrowsNdjsonException()
    {
        // Valid first record, truncated second record (missing closing brace)
        var input = "{\"ok\":true}\n{\"broken\":true\n";

        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(input));
        Assert.Contains("line 2", ex.Message);
    }

    [Fact]
    public void ReadRecords_NullBytesInInput_ThrowsNdjsonException()
    {
        // Null bytes embedded in a JSON line — invalid JSON
        var input = "{\"key\":\"val\x00ue\"}\n";

        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(input));
        Assert.Contains("line 1", ex.Message);
    }

    [Fact]
    public void ReadRecords_MixedValidAndInvalidLines_ThrowsOnFirstInvalid()
    {
        var input = "{\"a\":1}\n{\"b\":2}\nNOT_JSON\n{\"c\":3}\n";

        var ex = Assert.Throws<NdjsonException>(() => NdjsonReader.ReadRecords(input));
        Assert.Contains("line 3", ex.Message);
    }

    [Fact]
    public void ReadRecords_NullInput_ThrowsArgumentNull()
    {
        Assert.Throws<ArgumentNullException>(() => NdjsonReader.ReadRecords((string)null!));
    }

    [Fact]
    public void ReadRecords_OnlyWhitespaceLines_ReturnsEmpty()
    {
        var input = "   \n\t\n  \t  \n";
        var records = NdjsonReader.ReadRecords(input);
        Assert.Empty(records);
    }

    [Fact]
    public void ReadRecords_ArrayTopLevel_Parses()
    {
        // NDJSON allows any JSON value per line, not just objects
        var input = "[1,2,3]\n\"just a string\"\n42\nnull\ntrue\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Equal(5, records.Count);
        Assert.Equal(JsonValueKind.Array, records[0].ValueKind);
        Assert.Equal(JsonValueKind.String, records[1].ValueKind);
        Assert.Equal(JsonValueKind.Number, records[2].ValueKind);
        Assert.Equal(JsonValueKind.Null, records[3].ValueKind);
        Assert.Equal(JsonValueKind.True, records[4].ValueKind);
    }

    [Fact]
    public void ReadRecords_UnicodeEscapes_ParsedCorrectly()
    {
        var input = "{\"emoji\":\"\\u2764\",\"cjk\":\"\\u4E16\\u754C\"}\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Single(records);
        Assert.Equal("\u2764", records[0].GetProperty("emoji").GetString());
        Assert.Equal("\u4E16\u754C", records[0].GetProperty("cjk").GetString());
    }

    [Fact]
    public void ReadRecords_DuplicateKeys_LastWins()
    {
        // JSON spec allows duplicate keys; System.Text.Json keeps the last value
        var input = "{\"k\":1,\"k\":2}\n";
        var records = NdjsonReader.ReadRecords(input);

        Assert.Single(records);
        Assert.Equal(2, records[0].GetProperty("k").GetInt32());
    }
}
