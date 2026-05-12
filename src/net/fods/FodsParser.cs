// FormatFactory.Fods — Commercial .NET FODS Parser
// Gate 11 Skeleton — not release-ready
// DEC-033 Option B: .NET Commercial Only
// Python FOSS track: src/python/fods/ (Apache-2.0)

using System;
using System.Collections.Generic;
using System.Xml;

namespace FormatFactory.Fods;

/// <summary>
/// SKELETON: Gate 11 readiness. Full implementation pending Gate 11 approval.
/// Parses Flat OpenDocument Spreadsheet (FODS) files.
/// FODS is the flat-XML variant of ODF Spreadsheet (see ODF 1.3 Part 3).
/// Root element: office:spreadsheet
/// Namespace: urn:oasis:names:tc:opendocument:xmlns:table:1.0
/// </summary>
public class FodsParser
{
    // Tier 0 baseline: structured skeleton only
    // Full iterparse streaming implementation required before Gate 11 approval

    /// <summary>
    /// Parse a FODS file and return sheet names. Skeleton implementation.
    /// </summary>
    /// <param name="filePath">Absolute path to .fods file</param>
    /// <returns>List of sheet names (empty in skeleton)</returns>
    /// <exception cref="NotImplementedException">Full implementation pending Gate 11</exception>
    public IReadOnlyList<string> GetSheetNames(string filePath)
    {
        // SKELETON: validates file exists and is XML; does not extract data
        ArgumentNullException.ThrowIfNull(filePath);
        if (!System.IO.File.Exists(filePath))
            throw new System.IO.FileNotFoundException($"FODS file not found: {filePath}");

        // Validate it is well-formed XML (Tier 0 baseline check)
        using var reader = XmlReader.Create(filePath, new XmlReaderSettings
        {
            DtdProcessing = DtdProcessing.Prohibit,
            XmlResolver = null,
        });
        while (reader.Read()) { } // consume to validate well-formed

        // Full sheet enumeration: NOT IMPLEMENTED (Gate 11 skeleton)
        return Array.Empty<string>();
    }
}
