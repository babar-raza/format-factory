// Tests for ZST exception hierarchy (ZstWriteException, ZstFileSizeException, ZstFileNotFoundException).
// Sprint: ff-sprint-s143-dotnet-deepening-20260627
// Ledger: PC-ZST-R137

using System;
using System.IO;
using System.Text;
using Xunit;

namespace FormatFactory.Zst.Tests;

/// <summary>
/// R137: Tests for ZST exception class hierarchy.
/// ZstException is the base; subclasses ZstInvalidMagicException, ZstFileSizeException,
/// ZstFileNotFoundException, and ZstWriteException each carry message and inner exception.
/// Covers: ZstWriteException is subclass of ZstException; ZstWriteException message stored;
/// ZstFileSizeException is subclass of ZstException; ZstFileSizeException message stored;
/// ZstFileNotFoundException is subclass of ZstException; ZstFileNotFoundException message stored;
/// ZstException base constructor two-arg with inner; ZstFileSizeException inner exception stored;
/// ZstInvalidMagicException is subclass of ZstException;
/// dogfood Parse nonexistent file throws ZstFileNotFoundException.
/// </summary>
public class ZstR137ExceptionHierarchyTests
{
    // -------------------------------------------------------------------------
    // ZstWriteException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstWriteException_IsSubclassOfZstException()
    {
        var ex = new ZstWriteException("write failed");
        Assert.IsAssignableFrom<ZstException>(ex);
    }

    [Fact]
    public void ZstWriteException_MessageIsStored()
    {
        var ex = new ZstWriteException("disk full");
        Assert.Equal("disk full", ex.Message);
    }

    // -------------------------------------------------------------------------
    // ZstFileSizeException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstFileSizeException_IsSubclassOfZstException()
    {
        var ex = new ZstFileSizeException("file too large");
        Assert.IsAssignableFrom<ZstException>(ex);
    }

    [Fact]
    public void ZstFileSizeException_MessageIsStored()
    {
        var ex = new ZstFileSizeException("exceeds 256 MB limit");
        Assert.Equal("exceeds 256 MB limit", ex.Message);
    }

    [Fact]
    public void ZstFileSizeException_WithInnerException_InnerStored()
    {
        var inner = new InvalidOperationException("inner");
        var ex = new ZstFileSizeException("outer", inner);
        Assert.Same(inner, ex.InnerException);
    }

    // -------------------------------------------------------------------------
    // ZstFileNotFoundException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstFileNotFoundException_IsSubclassOfZstException()
    {
        var ex = new ZstFileNotFoundException("file not found");
        Assert.IsAssignableFrom<ZstException>(ex);
    }

    [Fact]
    public void ZstFileNotFoundException_MessageIsStored()
    {
        var ex = new ZstFileNotFoundException("no such file");
        Assert.Equal("no such file", ex.Message);
    }

    // -------------------------------------------------------------------------
    // ZstInvalidMagicException hierarchy
    // -------------------------------------------------------------------------

    [Fact]
    public void ZstInvalidMagicException_IsSubclassOfZstException()
    {
        var ex = new ZstInvalidMagicException("bad magic bytes");
        Assert.IsAssignableFrom<ZstException>(ex);
    }

    // -------------------------------------------------------------------------
    // Dogfood: Parse nonexistent file -> ZstFileNotFoundException
    // -------------------------------------------------------------------------

    [Fact]
    public void DogfoodPipeline_ParseNonexistentFile_ThrowsZstFileNotFoundException()
    {
        var path = Path.Combine(Path.GetTempPath(), $"nonexistent_{Guid.NewGuid():N}.zst");
        Assert.Throws<ZstFileNotFoundException>(() => ZstParser.Parse(path));
    }
}
