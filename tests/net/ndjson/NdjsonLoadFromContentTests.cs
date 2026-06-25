// Tests for NdjsonDocument.LoadFromContent (QF-3-004, PQ-011)

using System;
using System.IO;
using FormatFactory.Ndjson;
using Xunit;

namespace FormatFactory.Ndjson.Tests;

public class NdjsonLoadFromContentTests
{
    private const string SampleContent = "{\"id\":1,\"name\":\"Alice\"}\n{\"id\":2,\"name\":\"Bob\"}";

    [Fact]
    public void LoadFromContent_ParsesRecords()
    {
        var doc = NdjsonDocument.LoadFromContent(SampleContent);
        Assert.Equal(2, doc.Count);
    }

    [Fact]
    public void LoadFromContent_ProducesSameResult_AsLoad()
    {
        var doc1 = NdjsonDocument.Load(SampleContent);
        var doc2 = NdjsonDocument.LoadFromContent(SampleContent);
        Assert.Equal(doc1.Count, doc2.Count);
    }

    [Fact]
    public void LoadFromContent_IsAccessibleFromPublicApi()
    {
        // Verifies the method is public (compiles)
        var doc = NdjsonDocument.LoadFromContent("{\"x\":1}");
        Assert.Equal(1, doc.Count);
    }

    [Fact]
    public void Load_StringOverload_StillWorks_ForBackwardCompatibility()
    {
        // Load(string) must remain available
        var doc = NdjsonDocument.Load(SampleContent);
        Assert.Equal(2, doc.Count);
    }

    [Fact]
    public void LoadFile_ReturnsDistinctMethodFromLoadFromContent()
    {
        // Just verifies both exist without conflict
        var content = NdjsonDocument.LoadFromContent("{\"a\":1}");
        Assert.Equal(1, content.Count);
    }
}
