// FormatFactory.Tsv — TSV Writer
// commercial_product_ready: false

using System.Text;

namespace FormatFactory.Tsv;

/// <summary>
/// Writes tab-separated values to strings or files.
///
/// Behaviour:
///   - Joins fields with tab character, rows with LF.
///   - Null fields are treated as empty strings.
///   - Validates that fields do not contain tab or newline characters.
///   - Outputs UTF-8 without BOM.
///
/// MWP status: minimal viable product.
/// </summary>
public static class TsvWriter
{
    /// <summary>
    /// Serialize rows to a TSV string.
    /// </summary>
    /// <param name="rows">Rows of fields. Null fields are treated as empty strings.</param>
    /// <returns>TSV content as a string with LF line endings.</returns>
    /// <exception cref="TsvException">Thrown when a field contains a tab or newline character.</exception>
    public static string WriteRows(IEnumerable<IEnumerable<string?>> rows)
    {
        ArgumentNullException.ThrowIfNull(rows);

        var sb = new StringBuilder();
        foreach (var row in rows)
        {
            var fields = new List<string>();
            foreach (var field in row)
            {
                var value = field ?? string.Empty;
                ValidateField(value);
                fields.Add(value);
            }
            sb.Append(string.Join("\t", fields));
            sb.Append('\n');
        }
        return sb.ToString();
    }

    /// <summary>
    /// Serialize rows and write to a file. UTF-8, no BOM.
    /// Creates parent directories as needed.
    /// </summary>
    public static void WriteRowsToFile(IEnumerable<IEnumerable<string?>> rows, string path)
    {
        ArgumentNullException.ThrowIfNull(rows);
        if (string.IsNullOrWhiteSpace(path))
            throw new TsvException("path must not be null or empty.");

        var dir = Path.GetDirectoryName(path);
        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);

        var content = WriteRows(rows);
        File.WriteAllText(path, content, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));
    }

    // -------------------------------------------------------------------------
    // Validation
    // -------------------------------------------------------------------------

    private static void ValidateField(string value)
    {
        if (value.Contains('\t'))
            throw new TsvException($"Field contains a tab character which is not allowed in TSV fields: \"{Truncate(value)}\"");
        if (value.Contains('\n') || value.Contains('\r'))
            throw new TsvException($"Field contains a newline character which is not allowed in TSV fields: \"{Truncate(value)}\"");
    }

    private static string Truncate(string value, int maxLength = 50)
    {
        if (value.Length <= maxLength) return value;
        return value[..maxLength] + "...";
    }
}
