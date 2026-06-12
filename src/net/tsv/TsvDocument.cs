// FormatFactory.Tsv — TSV Document model
// commercial_product_ready: false

namespace FormatFactory.Tsv;

/// <summary>
/// Simple in-memory TSV document with optional headers.
///
/// Usage:
///   var doc = TsvDocument.Load("Name\tAge\nAlice\t30\n");
///   Console.WriteLine(doc.Headers![0]); // "Name"
///   Console.WriteLine(doc.Rows[0][1]);  // "30"
///
/// MWP status: minimal viable product.
/// </summary>
public class TsvDocument
{
    /// <summary>Header row (first row), or null if HasHeaders is false.</summary>
    public string[]? Headers { get; set; }

    /// <summary>Data rows (excludes header row when HasHeaders is true).</summary>
    public List<string[]> Rows { get; set; } = new();

    /// <summary>Whether the document has a header row.</summary>
    public bool HasHeaders { get; set; }

    /// <summary>Number of data rows (excluding headers).</summary>
    public int RowCount => Rows.Count;

    /// <summary>
    /// Number of columns, determined from headers (if present) or the first data row.
    /// Returns 0 if the document is empty.
    /// </summary>
    public int ColumnCount
    {
        get
        {
            if (Headers is not null && Headers.Length > 0) return Headers.Length;
            if (Rows.Count > 0) return Rows[0].Length;
            return 0;
        }
    }

    /// <summary>Load a TSV document from a string.</summary>
    /// <param name="content">TSV content.</param>
    /// <param name="hasHeaders">If true, the first row is treated as headers.</param>
    public static TsvDocument Load(string content, bool hasHeaders = true)
    {
        var allRows = TsvReader.ReadRows(content);
        return BuildDocument(allRows, hasHeaders);
    }

    /// <summary>Load a TSV document from a file.</summary>
    /// <param name="path">Path to the TSV file.</param>
    /// <param name="hasHeaders">If true, the first row is treated as headers.</param>
    public static TsvDocument LoadFile(string path, bool hasHeaders = true)
    {
        var allRows = TsvReader.ReadRowsFromFile(path);
        return BuildDocument(allRows, hasHeaders);
    }

    /// <summary>Serialize the document back to a TSV string.</summary>
    public string ToTsv()
    {
        var allRows = new List<IEnumerable<string?>>();

        if (HasHeaders && Headers is not null)
            allRows.Add(Headers);

        foreach (var row in Rows)
            allRows.Add(row);

        return TsvWriter.WriteRows(allRows);
    }

    /// <summary>Save the document to a file. UTF-8, no BOM.</summary>
    public void SaveToFile(string path)
    {
        var allRows = new List<IEnumerable<string?>>();

        if (HasHeaders && Headers is not null)
            allRows.Add(Headers);

        foreach (var row in Rows)
            allRows.Add(row);

        TsvWriter.WriteRowsToFile(allRows, path);
    }

    // -------------------------------------------------------------------------
    // Internal
    // -------------------------------------------------------------------------

    private static TsvDocument BuildDocument(List<string[]> allRows, bool hasHeaders)
    {
        var doc = new TsvDocument { HasHeaders = hasHeaders };

        if (hasHeaders && allRows.Count > 0)
        {
            doc.Headers = allRows[0];
            doc.Rows = allRows.GetRange(1, allRows.Count - 1);
        }
        else
        {
            doc.Rows = allRows;
        }

        return doc;
    }
}
