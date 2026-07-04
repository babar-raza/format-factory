// FormatFactory.Fods — FodsWorksheetCollection
// Aspose-style collection of worksheets in a FODS document.
// Canonical model: FormatFactory.Fods.Model.Office.Spreadsheet (spec_qname: office:spreadsheet)
// Authority: plans/.claude/imperative-drifting-conway.md §1, §3
// TC-W1-FODS-NET-003

using System;
using System.Collections;
using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Aspose-style collection of worksheets in a FODS document.
/// Backed by the office:spreadsheet DOM element.
///
/// Access pattern (Aspose-style):
///   doc.Worksheets[0]         — by index
///   doc.Worksheets["Sheet1"]  — by name
///   doc.Worksheets.Count
///   doc.Worksheets.Add("New")
///   doc.Worksheets.Remove("Old")
///
/// Canonical model: <see cref="FormatFactory.Fods.Model.Office.Spreadsheet"/>
/// spec_qname: office:spreadsheet (container), table:table (element)
/// ODF 1.3 §3.7, §9.1.2
/// </summary>
public sealed class FodsWorksheetCollection : IReadOnlyList<FodsWorksheet>
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    private readonly XElement _spreadsheetElement;

    internal FodsWorksheetCollection(XElement spreadsheetElement)
    {
        _spreadsheetElement = spreadsheetElement
            ?? throw new ArgumentNullException(nameof(spreadsheetElement));
    }

    // -------------------------------------------------------------------------
    // Count
    // -------------------------------------------------------------------------

    /// <summary>Number of worksheets (table:table elements) in this document.</summary>
    public int Count
    {
        get
        {
            var count = 0;
            foreach (var _ in _spreadsheetElement.Elements(NsTable + "table"))
                count++;
            return count;
        }
    }

    // -------------------------------------------------------------------------
    // Indexers — by index and by name
    // -------------------------------------------------------------------------

    /// <summary>
    /// Get a worksheet by zero-based index.
    /// Throws <see cref="ArgumentOutOfRangeException"/> if the index is out of range.
    /// spec_qname: table:table
    /// </summary>
    public FodsWorksheet this[int index]
    {
        get
        {
            if (index < 0) throw new ArgumentOutOfRangeException(nameof(index));
            var i = 0;
            foreach (var el in _spreadsheetElement.Elements(NsTable + "table"))
            {
                if (i == index) return new FodsWorksheet(el);
                i++;
            }
            throw new ArgumentOutOfRangeException(nameof(index),
                $"Index {index} is out of range; document has {i} worksheet(s).");
        }
    }

    /// <summary>
    /// Get a worksheet by name (case-sensitive).
    /// Throws <see cref="ArgumentException"/> if no sheet with that name exists.
    /// spec_qname: table:table / table:name attribute
    /// </summary>
    public FodsWorksheet this[string name]
    {
        get
        {
            if (string.IsNullOrEmpty(name))
                throw new ArgumentException("Worksheet name must not be null or empty.", nameof(name));

            foreach (var el in _spreadsheetElement.Elements(NsTable + "table"))
            {
                if (el.Attribute(NsTable + "name")?.Value == name)
                    return new FodsWorksheet(el);
            }

            throw new ArgumentException(
                $"No worksheet named '{name}' exists in this document.", nameof(name));
        }
    }

    // -------------------------------------------------------------------------
    // Add / Remove
    // -------------------------------------------------------------------------

    /// <summary>
    /// Append a new empty worksheet with the given name.
    /// Throws <see cref="InvalidOperationException"/> if a sheet with the same name exists.
    /// spec_qname: table:table / table:name attribute
    /// </summary>
    public FodsWorksheet Add(string name)
    {
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Worksheet name must not be null or empty.", nameof(name));

        foreach (var existing in _spreadsheetElement.Elements(NsTable + "table"))
        {
            if (existing.Attribute(NsTable + "name")?.Value == name)
                throw new InvalidOperationException(
                    $"A worksheet named '{name}' already exists.");
        }

        var tableEl = new XElement(NsTable + "table",
            new XAttribute(NsTable + "name", name));
        _spreadsheetElement.Add(tableEl);
        return new FodsWorksheet(tableEl);
    }

    /// <summary>
    /// Remove the worksheet with the given name.
    /// Throws <see cref="ArgumentException"/> if no sheet with that name exists.
    /// </summary>
    public void Remove(string name)
    {
        if (string.IsNullOrEmpty(name))
            throw new ArgumentException("Worksheet name must not be null or empty.", nameof(name));

        foreach (var el in _spreadsheetElement.Elements(NsTable + "table"))
        {
            if (el.Attribute(NsTable + "name")?.Value == name)
            {
                el.Remove();
                return;
            }
        }

        throw new ArgumentException(
            $"No worksheet named '{name}' exists in this document.", nameof(name));
    }

    // -------------------------------------------------------------------------
    // Enumeration (IReadOnlyList<FodsWorksheet>)
    // -------------------------------------------------------------------------

    /// <summary>Enumerate all worksheets in document order.</summary>
    public IEnumerator<FodsWorksheet> GetEnumerator()
    {
        foreach (var el in _spreadsheetElement.Elements(NsTable + "table"))
            yield return new FodsWorksheet(el);
    }

    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}
