// FormatFactory.Fods — FodsWorksheet
// Public API wrapper for a single ODF spreadsheet sheet (table:table).
// Aspose-style: FodsDocument.Worksheets[i] returns FodsWorksheet.
// Canonical model: FormatFactory.Fods.Model.Table.Table (spec_qname: table:table)
// Authority: plans/.claude/imperative-drifting-conway.md §1, §3
// TC-W1-FODS-NET-003

using System;
using System.Collections.Generic;
using System.Xml.Linq;

namespace FormatFactory.Fods;

/// <summary>
/// Public API wrapper for a single ODF table:table element (a spreadsheet sheet/tab).
/// Backed by the live XElement in the DOM — mutations write through to the document.
///
/// Aspose-style navigation:
///   FodsDocument.Worksheets → FodsWorksheetCollection → FodsWorksheet → FodsRow → FodsCell
///
/// Canonical model: <see cref="FormatFactory.Fods.Model.Table.Table"/>
/// spec_qname: table:table
/// ODF 1.3 §9.1.2
/// </summary>
public sealed class FodsWorksheet
{
    private static readonly XNamespace NsTable =
        "urn:oasis:names:tc:opendocument:xmlns:table:1.0";

    internal XElement Element { get; }

    internal FodsWorksheet(XElement element)
    {
        Element = element;
    }

    // -------------------------------------------------------------------------
    // Name — table:name attribute
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets or sets the worksheet name (table:name attribute).
    /// ODF 1.3 §9.1.2 — table:name is required.
    /// spec_qname: table:table
    /// </summary>
    public string Name
    {
        get => Element.Attribute(NsTable + "name")?.Value ?? string.Empty;
        set => Element.SetAttributeValue(NsTable + "name", value);
    }

    // -------------------------------------------------------------------------
    // Rows — FodsRowCollection
    // ODF 1.3 §9.4.4: table:table-row children of table:table
    // -------------------------------------------------------------------------

    /// <summary>
    /// All rows in this worksheet (table:table-row elements), in document order.
    /// Each row exposes <see cref="FodsRow.Cells"/> for cell access.
    ///
    /// spec_qname: table:table-row (child QName)
    /// ODF 1.3 §9.4.4
    /// </summary>
    public IReadOnlyList<FodsRow> Rows
    {
        get
        {
            var result = new List<FodsRow>();
            foreach (var child in Element.Elements(NsTable + "table-row"))
                result.Add(new FodsRow(child));
            return result;
        }
    }

    // -------------------------------------------------------------------------
    // Display / Visibility
    // -------------------------------------------------------------------------

    /// <summary>
    /// Gets or sets the sheet visibility (table:display attribute).
    /// True = visible (default); false = hidden.
    /// ODF 1.3 §9.1.2
    /// </summary>
    public bool IsVisible
    {
        get
        {
            var display = Element.Attribute(NsTable + "display")?.Value;
            return display == null || !string.Equals(display, "false",
                StringComparison.OrdinalIgnoreCase);
        }
        set => Element.SetAttributeValue(NsTable + "display", value ? "true" : "false");
    }

    // -------------------------------------------------------------------------
    // FodsSheet compatibility — exposes the underlying XElement via FodsSheet
    // -------------------------------------------------------------------------

    /// <summary>
    /// Returns this worksheet as a <see cref="FodsSheet"/> (legacy DOM wrapper).
    /// Provided for backward compatibility during migration.
    /// Prefer the <see cref="Rows"/> property for new code.
    /// </summary>
    internal FodsSheet AsSheet() => new FodsSheet(Element);
}
