// Tests for CsvWriter.WriteRowsToFile() file-write static API.
// Sprint: FORMAT-FACTORY-CSV-WRITEROWS-TOFILE-R124-20260627
// Ledger: R124-GOVERNED-DOTNET-CSV-WRITEROWS-TOFILE-001

using System;
using System.Collections.Generic;
using System.IO;
using Xunit;

namespace FormatFactory.Csv.Tests;

/// <summary>
/// R124: CsvWriter.WriteRowsToFile(rows, path) writes raw string rows to a CSV file.
/// The output file: exists after write, contains comma separators, preserves all
/// cell values, uses UTF-8 without BOM, produces no CRLF line endings. Null path
/// throws CsvWriterException. The file content round-trips back via CsvReader.ReadRowsFromFile.
/// </summary>
public class CsvR124WriteRowsToFileTests
{
    private static string TempPath() =>
        Path.Combine(Path.GetTempPath(), $"ff_csv_r124_{Guid.NewGuid():N}.csv");

    private static IEnumerable<IEnumerable<string?>> SimpleRows() =>
        new List<IEnumerable<string?>>
        {
            new[] { "Name", "Age", "City" },
            new[] { "Alice", "30", "New York" },
            new[] { "Bob",   "25", "London"   },
        };

    // ---- File existence ----

    [Fact]
    public void WriteRowsToFile_ValidPath_CreatesFile()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            Assert.True(File.Exists(path));
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Content: commas and values ----

    [Fact]
    public void WriteRowsToFile_Output_ContainsCommas()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains(",", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_Output_ContainsHeaderValues()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("Name", content);
            Assert.Contains("Age",  content);
            Assert.Contains("City", content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_Output_ContainsDataValues()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var content = File.ReadAllText(path);
            Assert.Contains("Alice",    content);
            Assert.Contains("30",       content);
            Assert.Contains("New York", content);
            Assert.Contains("Bob",      content);
            Assert.Contains("London",   content);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Encoding ----

    [Fact]
    public void WriteRowsToFile_Encoding_NoUtf8Bom()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var bytes = File.ReadAllBytes(path);
            Assert.False(bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF,
                "Output must not contain a UTF-8 BOM");
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Round-trip: WriteRowsToFile → ReadRowsFromFile ----

    [Fact]
    public void WriteRowsToFile_RoundTrip_RowCountPreserved()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var reread = CsvReader.ReadRowsFromFile(path);
            Assert.Equal(3, reread.Count); // header + 2 data rows
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_RoundTrip_FirstRowValuesPreserved()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var reread = CsvReader.ReadRowsFromFile(path);
            Assert.Equal("Name", reread[0][0]);
            Assert.Equal("Age",  reread[0][1]);
            Assert.Equal("City", reread[0][2]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    [Fact]
    public void WriteRowsToFile_RoundTrip_DataRowValuesPreserved()
    {
        var path = TempPath();
        try
        {
            CsvWriter.WriteRowsToFile(SimpleRows(), path);
            var reread = CsvReader.ReadRowsFromFile(path);
            Assert.Equal("Alice",    reread[1][0]);
            Assert.Equal("30",       reread[1][1]);
            Assert.Equal("New York", reread[1][2]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }

    // ---- Null path throws ----

    [Fact]
    public void WriteRowsToFile_NullPath_ThrowsCsvWriterException()
    {
        Assert.Throws<CsvWriterException>(() =>
            CsvWriter.WriteRowsToFile(SimpleRows(), null!));
    }

    // ---- Dogfood: sales report pipeline ----

    [Fact]
    public void DogfoodPipeline_SalesReport_FileContainsAllData()
    {
        var path = TempPath();
        try
        {
            var rows = new List<IEnumerable<string?>>
            {
                new[] { "Product",   "Units", "Revenue"  },
                new[] { "Widget A",  "120",   "2400.00"  },
                new[] { "Widget B",  "85",    "4250.00"  },
                new[] { "Widget C",  "200",   "6000.00"  },
                new[] { "Total",     "405",   "12650.00" },
            };

            CsvWriter.WriteRowsToFile(rows, path);

            var content = File.ReadAllText(path);
            Assert.Contains("Product",   content);
            Assert.Contains("Widget A",  content);
            Assert.Contains("Widget C",  content);
            Assert.Contains("12650.00",  content);

            // Round-trip check
            var reread = CsvReader.ReadRowsFromFile(path);
            Assert.Equal(5, reread.Count);
            Assert.Equal("Widget B", reread[2][0]);
        }
        finally { if (File.Exists(path)) File.Delete(path); }
    }
}
